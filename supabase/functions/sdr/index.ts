// supabase/functions/sdr/index.ts
//
// O funil do SDR, ao vivo do Pipedrive:  Conectado -> SQL -> OPS -> SAL
//
//   GET /sdr?de=2026-08-01&ate=2026-08-31
//
// Por que uma função separada da `live`, e não mais um pedaço dela:
//
//   1. A `live` serve cinco páginas em produção. Mexer nela para acrescentar
//      uma página nova é arriscar o que já funciona.
//   2. A API v2 do Pipedrive aceita no máximo 15 campos customizados por
//      chamada, e a lista da `live` está em 15/15. "Data Conexão" não caberia
//      sem tirar outro campo de lá.
//   3. O limite de 15 é POR CHAMADA. Uma função separada tem os seus próprios
//      15 — e esta aqui nem chega perto, porque usa só a rota v1.
//
// A rota v1 (timeline por data de criação) devolve o negócio com TODOS os
// campos customizados, sem limite nenhum. É o que torna esta função simples:
// não existe "campo que não chegou".
//
// Ela busca pelos negócios ATUALIZADOS no período: preencher um campo mexe no
// negócio, então o que aconteceu no período aparece — inclusive num lead antigo.

const PD_TOKEN = Deno.env.get("PIPEDRIVE_API_TOKEN")!;
const PD_BASE = (Deno.env.get("PIPEDRIVE_BASE_URL") ?? "https://api.pipedrive.com").replace(/\/+$/, "");

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "authorization, x-client-info, apikey, content-type",
  "access-control-allow-methods": "GET, POST, OPTIONS",
};

const CAMPOS = {
  sdr:         "966e0b1c6e28cbb30fb6d82394746d33da5c07ea",  // Vendedor SDR
  vendedor:    "db2c9632937b836eae914bb3749d19f3b129b31d",  // o closer
  lead:        "1cb9ad4729d5f241f8a329045613582070ee2c95",  // Lead (A–F), do formulário
  leadSql:     "44a8dc2ef746c237899ea6f96f802b7b275874a2",  // Lead - SQL, a requalificação do SDR
  canalConex:  "a029b05c61e5a5c143d5c5fab5c440d622b3169f",
  origemContr: "e686706d165184efa332298cdc2bd737571952fe",
  dConexao:    "c527b5a136e4e64856851d721785b39b5f9274ae",  // "Dia em que foi conseguido contato com o Lead"
  dSql:        "7382f9db5de1930988bc7acbd676abaa4079a015",  // Data Qualificação (SQL)
  dOpp:        "395bf927e670b580aa5d012e9f242defca9f3050",  // Dia Oportunidade
  dSal:        "62df15f8b5a4071a910ee37b0a4b4654afbc48db",  // Data Lead Aceito pelo Closer (SAL)
} as const;

/* Os campos que o v2 tem que devolver. O teto é 15 por chamada; aqui são dez. */
const CAMPOS_V2 = [
  CAMPOS.sdr, CAMPOS.vendedor, CAMPOS.lead, CAMPOS.leadSql,
  CAMPOS.canalConex, CAMPOS.origemContr,
  CAMPOS.dConexao, CAMPOS.dSql, CAMPOS.dOpp, CAMPOS.dSal,
].join(",");

const pausa = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function pd(caminho: string, tentativa = 1): Promise<any> {
  const r = await fetch(`${PD_BASE}${caminho}`, {
    headers: { "x-api-token": PD_TOKEN, accept: "application/json" },
  });
  if ((r.status === 429 || r.status >= 500) && tentativa <= 4) {
    await pausa(800 * tentativa);
    return pd(caminho, tentativa + 1);
  }
  if (!r.ok) throw new Error(`Pipedrive ${r.status} em ${caminho}: ${await r.text()}`);

  /* Corpo vazio com status 2xx.
     ===========================
     Acontece: o Pipedrive engasga e devolve 200 sem nada dentro. Antes isto
     virava "Unexpected end of JSON input" — mensagem que não diz QUAL chamada
     falhou, e sem isso não dá para consertar nem para saber se é transitório.

     É transitório, então tenta de novo. Se insistir, o erro passa a dizer o
     endereço e o começo do que veio. */
  const txt = await r.text();
  if (!txt.trim()) {
    if (tentativa <= 4) { await pausa(800 * tentativa); return pd(caminho, tentativa + 1); }
    throw new Error(`Pipedrive devolveu ${r.status} com o corpo VAZIO em ${caminho} ` +
                    `(${tentativa} tentativas). Costuma ser instabilidade do Pipedrive.`);
  }
  try { return JSON.parse(txt); }
  catch {
    throw new Error(`Pipedrive devolveu ${r.status} com corpo ilegível em ${caminho}: ` +
                    txt.slice(0, 200));
  }
}

/* ---------- leitura de campos ---------- */
const cru = (v: any) => (v && typeof v === "object" ? (v.id ?? v.value ?? null) : (v ?? null));
const num = (v: any): number | null => {
  if (v === null || v === undefined || v === "") return null;
  if (typeof v === "object") return num(v.value ?? v.amount ?? null);
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};
const dia = (v: any) => (typeof v === "string" && v.length >= 10 ? v.slice(0, 10) : null);
const cf = (d: any, h: string) => d?.custom_fields?.[h] ?? d?.[h] ?? null;

/* ---------- metadados ---------- */
type Meta = {
  rotulos: Map<string, Map<string, string>>;
  usuarios: Map<number, string>;
  em: number;
};
let META: Meta | null = null;
const META_TTL = 10 * 60_000;

async function meta(): Promise<Meta> {
  if (META && Date.now() - META.em < META_TTL) return META;
  const rotulos = new Map<string, Map<string, string>>();
  // limit=500: com o padrão de 100 os rótulos de "Lead (A–F)" somem e a
  // qualificação inteira vira null.
  const campos = await pd("/api/v1/dealFields?start=0&limit=500");
  for (const f of campos.data ?? []) {
    if (!f.options?.length) continue;
    const m = new Map<string, string>();
    for (const o of f.options) m.set(String(o.id), o.label);
    rotulos.set(f.key, m);
  }
  const usuarios = new Map<number, string>();
  for (let start = 0; ; start += 500) {
    const r = await pd(`/api/v1/users?start=${start}&limit=500`);
    for (const u of r.data ?? []) usuarios.set(u.id, u.name);
    if (!r.additional_data?.pagination?.more_items_in_collection) break;
  }
  META = { rotulos, usuarios, em: Date.now() };
  return META;
}

function rot(m: Meta, campo: string, v: any): string | null {
  const b = cru(v);
  if (b === null || b === undefined || b === "") return null;
  const achado = m.rotulos.get(campo)?.get(String(b));
  if (achado) return achado;
  return typeof b === "string" && !/^\d+$/.test(b) ? b : null;
}
const nomeUsuario = (m: Meta, v: any) => {
  const id = num(cru(v));
  return id != null ? (m.usuarios.get(id) ?? null) : null;
};

/* ---------- a busca ----------
   ==============================
   Pelos negócios ATUALIZADOS no período, e não pelos criados nele.

   A pergunta é sobre datas que o time preenche: conexão, SQL, oportunidade,
   SAL. Um negócio que teve a Data Conexão preenchida em agosto foi, por
   definição, editado em agosto — não tem como preencher um campo sem mexer no
   negócio. Então pedir "o que foi mexido no período" pega tudo, inclusive o
   lead criado em março que só agora foi conectado.

   A primeira versão buscava por data de CRIAÇÃO, com uma janela de 90 dias
   para trás. Lia 15.643 negócios para ficar com 559, e ainda assim perdia os
   antigos: dava 539 conectados onde o Insights mostrava 956.

   Sim, `updated_since` é o mesmo parâmetro que derrubou a carteira aberta de
   124 para 37 na função `live`. Lá estava errado, e o motivo importa: a
   carteira precisa mostrar negócio antigo e PARADO, que por definição não foi
   atualizado. Aqui é o oposto — a pergunta é sobre coisas que aconteceram no
   período, e coisa que aconteceu deixa marca. */
type Linha = {
  id: number; t: string; sdr: string; v: string;
  dConexao: string | null; dSql: string | null; dOpp: string | null; dSal: string | null;
  lead: string | null;               // como o lead CHEGOU, pelo formulário
  leadSql: string | null;            // como ficou depois da requalificação do SDR
  canal: string | null; orig: string | null;
  s: "won" | "lost" | "open"; val: number; dCriacao: string | null;
};

async function buscar(m: Meta, de: string, ate: string) {
  const linhas: Linha[] = [];
  const vistos = new Set<number>();
  let cursor: string | null = null;
  let paginas = 0, brutos = 0, truncado = false;

  const noPeriodo = (x: string | null) => !!x && x >= de && x <= ate;

  for (let i = 0; i < 40; i++) {
    const q = new URLSearchParams({
      limit: "500",
      updated_since: de + "T00:00:00Z",
      custom_fields: CAMPOS_V2,
    });
    if (cursor) q.set("cursor", cursor);
    let r: any;
    try { r = await pd(`/api/v2/deals?${q}`); }
    catch { truncado = true; break; }

    const lote = r.data ?? [];
    paginas++; brutos += lote.length;

    for (const d of lote) {
      if (vistos.has(d.id)) continue;
      vistos.add(d.id);

      /* Descartado aqui dentro se não participa de nenhuma etapa no período.
         Guardar tudo e filtrar no fim foi o que matou a versão anterior com
         WORKER_RESOURCE_LIMIT antes de ela responder qualquer coisa. */
      const dConexao = dia(cf(d, CAMPOS.dConexao));
      const dSql = dia(cf(d, CAMPOS.dSql));
      const dOpp = dia(cf(d, CAMPOS.dOpp));
      const dSal = dia(cf(d, CAMPOS.dSal));
      if (!noPeriodo(dConexao) && !noPeriodo(dSql) && !noPeriodo(dOpp) && !noPeriodo(dSal)) continue;

      const status: Linha["s"] =
        d.status === "won" ? "won" : d.status === "lost" ? "lost" : "open";
      linhas.push({
        id: d.id,
        t: d.title ?? "(sem título)",
        sdr: nomeUsuario(m, cf(d, CAMPOS.sdr)) ?? "Sem SDR",
        v: nomeUsuario(m, cf(d, CAMPOS.vendedor)) ?? "Sem closer",
        dConexao, dSql, dOpp, dSal,
        lead: rot(m, CAMPOS.lead, cf(d, CAMPOS.lead)),
        leadSql: rot(m, CAMPOS.leadSql, cf(d, CAMPOS.leadSql)),
        canal: rot(m, CAMPOS.canalConex, cf(d, CAMPOS.canalConex)),
        orig: rot(m, CAMPOS.origemContr, cf(d, CAMPOS.origemContr)),
        s: status,
        val: num(d.value) ?? 0,
        dCriacao: dia(d.add_time),
      });
    }
    lote.length = 0;

    cursor = r.additional_data?.next_cursor ?? r.next_cursor ?? null;
    if (!cursor) break;
    if (i === 39) truncado = true;
  }
  return { linhas, brutos, paginas, truncado };
}

/* ---------- handler ---------- */
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  const t0 = Date.now();
  try {
    if (!PD_TOKEN) throw new Error("Falta o secret PIPEDRIVE_API_TOKEN");

    const url = new URL(req.url);
    const hoje = new Date().toISOString().slice(0, 10);
    const ate = url.searchParams.get("ate") ?? hoje;
    const de = url.searchParams.get("de") ??
      new Date(Date.parse(ate) - 29 * 86400000).toISOString().slice(0, 10);
    if (de > ate) throw new Error("Período invertido: 'de' é maior que 'ate'");

    const m = await meta();
    const { linhas, brutos, paginas, truncado } = await buscar(m, de, ate);

    /* Cada etapa é contada pela SUA data dentro do período — não pela data de
       criação do negócio. É assim que o Insights conta, e é o que faz o número
       bater: o card "Conectados" filtra por Data Conexão, não por criação. */
    const noPeriodo = (x: string | null) => !!x && x >= de && x <= ate;

    const conectados = linhas.filter((d) => noPeriodo(d.dConexao));
    const sql        = linhas.filter((d) => noPeriodo(d.dSql));
    const ops        = linhas.filter((d) => noPeriodo(d.dOpp));
    const sal        = linhas.filter((d) => noPeriodo(d.dSal));

    // `linhas` já vem só com quem participa de alguma etapa — o descarte
    // acontece dentro do laço da busca, senão a função morre antes de chegar aqui.
    const negocios = linhas;

    const avisos: string[] = [];
    if (truncado) avisos.push(
      `A varredura bateu no teto de páginas — os números podem estar incompletos.`);
    if (!conectados.length) avisos.push(
      `Nenhum negócio com <b>Data Conexão</b> no período. Confira se o campo está sendo preenchido.`);
    const semSdr = conectados.filter((d) => d.sdr === "Sem SDR").length;
    if (semSdr) avisos.push(
      `${semSdr} conectado(s) <b>sem o campo "Vendedor SDR"</b> — aparecem agrupados como "Sem SDR".`);

    return Response.json({
      ok: true,
      periodo: { de, ate },
      geradoEm: new Date().toISOString(),
      ms: Date.now() - t0,
      contagem: {
        conectados: conectados.length,
        sql: sql.length,
        ops: ops.length,
        sal: sal.length,
        negocios: negocios.length,
      },
      // o que a varredura leu de fato — responde "por que veio menos do que eu esperava"
      // o que a varredura leu de fato — responde "por que veio menos do que eu esperava"
      varredura: { de, ate, paginas, brutos, lidos: linhas.length, truncado },
      avisos,
      negocios,
    }, { headers: CORS });
  } catch (e) {
    return Response.json(
      { ok: false, erro: e instanceof Error ? e.message : String(e), ms: Date.now() - t0 },
      { status: 500, headers: CORS },
    );
  }
});

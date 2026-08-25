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
// O preço é buscar mais negócio do que o período pede — ver JANELA abaixo.

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
  lead:        "1cb9ad4729d5f241f8a329045613582070ee2c95",  // Lead (A–F)
  canalConex:  "a029b05c61e5a5c143d5c5fab5c440d622b3169f",
  origemContr: "e686706d165184efa332298cdc2bd737571952fe",
  dConexao:    "c527b5a136e4e64856851d721785b39b5f9274ae",  // "Dia em que foi conseguido contato com o Lead"
  dSql:        "7382f9db5de1930988bc7acbd676abaa4079a015",  // Data Qualificação (SQL)
  dOpp:        "395bf927e670b580aa5d012e9f242defca9f3050",  // Dia Oportunidade
  dSal:        "62df15f8b5a4071a910ee37b0a4b4654afbc48db",  // Data Lead Aceito pelo Closer (SAL)
} as const;

/* Quanto tempo antes do período a busca precisa começar.
   ======================================================
   A busca é por DATA DE CRIAÇÃO do negócio, porque é o que a timeline do v1
   filtra. Mas a pergunta é sobre as datas de conexão, SQL, OPS e SAL, que
   acontecem DEPOIS da criação — às vezes muito depois.

   Um lead criado em março que o closer aceitou em agosto conta como SAL de
   agosto. Com uma janela curta ele simplesmente não seria lido, e o número
   viria menor do que o Insights sem ninguém entender por quê.

   180 dias cobre com folga o ciclo real. Aumentar isto custa memória e tempo,
   não precisão: o que passa de 180 é raro. */
const JANELA_DIAS = 180;

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
const atras = (iso: string, n: number) =>
  new Date(Date.parse(iso + "T12:00:00Z") - n * 86400000).toISOString().slice(0, 10);

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
   Em blocos de 3 meses, e cada negócio é reduzido aos nove campos que
   interessam ANTES de entrar no array. Guardar o negócio inteiro por meio ano
   de criação é o que estourou a memória da `live` quando ela tentou algo
   parecido — aqui o negócio bruto morre dentro do laço. */
type Linha = {
  id: number; t: string; sdr: string; v: string;
  dConexao: string | null; dSql: string | null; dOpp: string | null; dSal: string | null;
  lead: string | null; canal: string | null; orig: string | null;
  s: "won" | "lost" | "open"; val: number; dCriacao: string | null;
};

async function buscar(m: Meta, desde: string, ate: string) {
  const linhas: Linha[] = [];
  const vistos = new Set<number>();
  let brutos = 0, blocos = 0, truncado = false;

  // quantos meses cobrir, do início da janela até o fim do período
  const ini = new Date(Date.parse(desde + "T12:00:00Z"));
  ini.setUTCDate(1);
  const fim = new Date(Date.parse(ate + "T12:00:00Z"));
  const meses = (fim.getUTCFullYear() - ini.getUTCFullYear()) * 12
              + (fim.getUTCMonth() - ini.getUTCMonth()) + 1;

  for (let passo = 0; passo < meses; passo += 3) {
    const bloco = new Date(ini);
    bloco.setUTCMonth(bloco.getUTCMonth() + passo);
    const de = bloco.toISOString().slice(0, 10);
    blocos++;
    let lote: any[] = [];
    try {
      const q = new URLSearchParams({
        start_date: de, interval: "month", amount: String(Math.min(3, meses - passo)),
        field_key: "add_time", exclude_deleted_deals: "1",
      });
      const r = await pd(`/api/v1/deals/timeline?${q}`);
      lote = (r.data ?? []).flatMap((x: any) => x.deals ?? []);
    } catch { truncado = true; continue; }

    for (const d of lote) {
      brutos++;
      if (vistos.has(d.id)) continue;      // blocos podem se encostar
      vistos.add(d.id);
      const status: Linha["s"] =
        d.status === "won" ? "won" : d.status === "lost" ? "lost" : "open";
      linhas.push({
        id: d.id,
        t: d.title ?? "(sem título)",
        sdr: nomeUsuario(m, cf(d, CAMPOS.sdr)) ?? "Sem SDR",
        v: nomeUsuario(m, cf(d, CAMPOS.vendedor)) ?? "Sem closer",
        dConexao: dia(cf(d, CAMPOS.dConexao)),
        dSql: dia(cf(d, CAMPOS.dSql)),
        dOpp: dia(cf(d, CAMPOS.dOpp)),
        dSal: dia(cf(d, CAMPOS.dSal)),
        lead: rot(m, CAMPOS.lead, cf(d, CAMPOS.lead)),
        canal: rot(m, CAMPOS.canalConex, cf(d, CAMPOS.canalConex)),
        orig: rot(m, CAMPOS.origemContr, cf(d, CAMPOS.origemContr)),
        s: status,
        val: num(d.value) ?? 0,
        dCriacao: dia(d.add_time),
      });
    }
    lote.length = 0;
  }
  return { linhas, brutos, blocos, truncado };
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
    const desde = atras(de, JANELA_DIAS);
    const { linhas, brutos, blocos, truncado } = await buscar(m, desde, ate);

    /* Cada etapa é contada pela SUA data dentro do período — não pela data de
       criação do negócio. É assim que o Insights conta, e é o que faz o número
       bater: o card "Conectados" filtra por Data Conexão, não por criação. */
    const noPeriodo = (x: string | null) => !!x && x >= de && x <= ate;
    const conectados = linhas.filter((d) => noPeriodo(d.dConexao));
    const sql        = linhas.filter((d) => noPeriodo(d.dSql));
    const ops        = linhas.filter((d) => noPeriodo(d.dOpp));
    const sal        = linhas.filter((d) => noPeriodo(d.dSal));

    /* Só sai daqui o negócio que participa de alguma etapa no período. O resto
       foi lido para poder ser descartado com segurança — mandar tudo para o
       navegador seria meio ano de negócios numa resposta. */
    const relevante = new Set<number>();
    for (const arr of [conectados, sql, ops, sal]) for (const d of arr) relevante.add(d.id);
    const negocios = linhas.filter((d) => relevante.has(d.id));

    const avisos: string[] = [];
    if (truncado) avisos.push(
      `Algum bloco da varredura falhou — os números podem estar incompletos. Recarregue.`);
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
      varredura: { desde, ate, janela_dias: JANELA_DIAS, blocos, brutos, lidos: linhas.length, truncado },
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

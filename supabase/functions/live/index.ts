// supabase/functions/live/index.ts
//
// Consulta o Pipedrive AO VIVO e devolve os negócios já normalizados para o painel.
// Não grava em tabela nenhuma — o Supabase entra só como porta de entrada, para o
// token do Pipedrive nunca sair do servidor (o navegador não pode chamar a API
// direto: o token ficaria visível no HTML e o Pipedrive bloqueia CORS).
//
//   GET /live?de=2026-08-01&ate=2026-08-20
//
// Recorte devolvido (união, sem repetir negócio):
//   · ganhos    -> won_time dentro do período
//   · perdidos  -> lost_time dentro do período
//   · criados   -> add_time dentro do período
//   · abertos   -> toda a carteira aberta hoje, independente de data
//
// O card [AE] Ganhos do Insights = status "won" + won_time no período,
// agrupado pelo campo "Vendedor". É esse número que este endpoint reproduz.

import { ehReuniao, melhorQue, type Escolha } from "./proxima.ts";

const PD_TOKEN = Deno.env.get("PIPEDRIVE_API_TOKEN")!;
const PD_BASE = (Deno.env.get("PIPEDRIVE_BASE_URL") ?? "https://api.pipedrive.com").replace(/\/+$/, "");

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "authorization, x-client-info, apikey, content-type",
  "access-control-allow-methods": "GET, POST, OPTIONS",
};

const CAMPOS = {
  vendedor:    "db2c9632937b836eae914bb3749d19f3b129b31d",
  sdr:         "966e0b1c6e28cbb30fb6d82394746d33da5c07ea",
  produto:     "6621eda2196194ded0bd671ae263ccbcb213666c",
  apresentado: "810aeffbcd6e447f89e9b82d1a977738a10f2f86",
  sugerido:    "1afa49dad1fa96c44b0f4d86fe08c5039f36fb1d",
  lead:        "1cb9ad4729d5f241f8a329045613582070ee2c95",
  leadSql:     "44a8dc2ef746c237899ea6f96f802b7b275874a2",
  temperatura: "41f8e1b82e5a22c2e9ad6febf44d7e7432d848d7",
  canalConex:  "a029b05c61e5a5c143d5c5fab5c440d622b3169f",
  canalQualif: "c35ba7a7cbb8b51bb3cbbd0a67021c4ee7fb8160",
  origemContr: "e686706d165184efa332298cdc2bd737571952fe",
  bu:          "e5a6564e575d47738856abf3d1c02611059761d6",
  marketplace: "0d3ea836c2e5b9fcdde94e9362e814dbec4e10d9",
  encontros:   "6d583650fab0b0084ba83cc37bf35b5915bfacd2",
  obsCall:     "86976faa3447d60899550bef228e2f06a95aa605",
  descPerda:   "c1056dfb2bc711a3a2dc66b4dc9c83a436a36a84",
  saude:       "57f999401867edd9e2b7e2cb6ec110b54846a870",
  dtCancel:    "2c29e719270fbfd6ecd08493148c39a00e0befba",
  dtSolic:     "cd0cc16e257579e4210871e5cfb26876b87c442b",
  motivoChurn: "9755e115e954e1c1328c81979d6d190434a444db",
  reembolso:   "77ee68c16f4760b4e17f6aafe4044996afc689f4",
  valorPago:   "bda2468564ef1c879c391b46bd96bd4034bae61d",
  nroRetornos: "ae214022c185ae7ff63ea20f1a9a9c08dc19e685",
  retAgendado: "3d8b962590bb3422ffcf9ea1c2ae3223ac1745e0",   // Data Retorno Agendado
  retRealizado:"ee1a9a6385a9484273a765926c2307bc667f8e6d",   // Data Retorno Realizado
  noShow:      "3f72c70e5276b453704bd0d0e75f767a48626449",   // Data NoShow
  diaOpp:      "395bf927e670b580aa5d012e9f242defca9f3050",
  diaReuniao:  "c8a99e668e9913e2362556c43a03bd821db81006",
  dataSal:     "62df15f8b5a4071a910ee37b0a4b4654afbc48db",
  dataSql:     "7382f9db5de1930988bc7acbd676abaa4079a015",
} as const;

const pausa = (ms: number) => new Promise((r) => setTimeout(r, ms));

// O v2 devolve o negócio inteiro por padrão. Pedindo só o que o painel usa, a
// resposta encolhe muito — foi o que estourou o limite de memória da função.
// O v2 aceita no máximo 15 campos customizados por chamada. Aqui entram só os
// que os PERDIDOS e os ABERTOS precisam — os ganhos vêm pela timeline (v1),
// que já devolve todos os campos, inclusive os de churn e valor pago.
const CAMPOS_V2 = [
  "db2c9632937b836eae914bb3749d19f3b129b31d", // Vendedor  (é o filtro do painel)
  "6621eda2196194ded0bd671ae263ccbcb213666c", // Produto
  "810aeffbcd6e447f89e9b82d1a977738a10f2f86", // Produto apresentado
  "1afa49dad1fa96c44b0f4d86fe08c5039f36fb1d", // Produto à ofertar
  "1cb9ad4729d5f241f8a329045613582070ee2c95", // Lead (A–F)
  "41f8e1b82e5a22c2e9ad6febf44d7e7432d848d7", // Temperatura
  "a029b05c61e5a5c143d5c5fab5c440d622b3169f", // Canal de conexão
  "3d8b962590bb3422ffcf9ea1c2ae3223ac1745e0", // Data retorno agendado
  "e686706d165184efa332298cdc2bd737571952fe", // Origem contratual
  "c1056dfb2bc711a3a2dc66b4dc9c83a436a36a84", // Descrição da perda
  "ae214022c185ae7ff63ea20f1a9a9c08dc19e685", // Nro de retornos
  "ee1a9a6385a9484273a765926c2307bc667f8e6d", // Data retorno realizado
  "57f999401867edd9e2b7e2cb6ec110b54846a870", // Saúde do aluno
  "2c29e719270fbfd6ecd08493148c39a00e0befba", // Data do cancelamento
  "3f72c70e5276b453704bd0d0e75f767a48626449", // Data no-show
].slice(0, 15).join(",");
// Canal de qualificação, Observação da call e Motivo do churn saíram daqui porque
// só interessam em negócio ganho — e ganho vem pela timeline do v1, com tudo.

// Paginação do v2 que descarta o que não interessa ainda dentro do laço —
// assim a função nunca segura milhares de negócios na memória de uma vez.
const truncou = new Set<string>();
/* Quanto cada varredura leu de fato. Sem isto não dá para distinguir "a conta
   só tem 29 negócios abertos com Vendedor" de "a paginação parou na página 1 e
   os outros 90 nunca foram lidos" — os dois casos produzem a mesma tela vazia,
   e o segundo é bug. Vai inteiro para a resposta. */
const DIAG_V2: Record<string, {
  paginas: number; brutos: number; mantidos: number; truncado: boolean;
}> = {};

async function paginaV2(status: "lost" | "open", extra: Record<string, string>,
                        manter: (d: any) => boolean, maxPaginas = 30) {
  const saida: any[] = [];
  let cursor: string | null = null;
  let paginas = 0, brutos = 0;
  for (let i = 0; i < maxPaginas; i++) {
    const q = new URLSearchParams({ limit: "500", status, custom_fields: CAMPOS_V2, ...extra });
    if (cursor) q.set("cursor", cursor);
    const r = await pd(`/api/v2/deals?${q}`);
    const lote = r.data ?? [];
    paginas++; brutos += lote.length;
    for (const d of lote) if (manter(d)) saida.push(d);
    // O v2 devolve o cursor em additional_data.next_cursor. Aceito também a
    // forma na raiz: se a API mudar de lugar, o laço parava calado na página 1
    // e a carteira aberta chegava pela metade sem ninguém perceber.
    cursor = r.additional_data?.next_cursor ?? r.next_cursor ?? null;
    if (!cursor) break;
  }
  // Truncou se saímos do laço com cursor ainda pendente — quer dizer que existe
  // negócio que nunca foi lido.
  if (cursor) truncou.add(status);
  DIAG_V2[status] = { paginas, brutos, mantidos: saida.length, truncado: !!cursor };
  return saida;
}

async function pd(caminho: string, tentativa = 1): Promise<any> {
  const r = await fetch(`${PD_BASE}${caminho}`, {
    headers: { "x-api-token": PD_TOKEN, accept: "application/json" },
  });
  if ((r.status === 429 || r.status >= 500) && tentativa <= 4) {
    await pausa(800 * tentativa);
    return pd(caminho, tentativa + 1);
  }
  if (!r.ok) throw new Error(`Pipedrive ${r.status} em ${caminho}: ${await r.text()}`);
  return r.json();
}

/* ---------- metadados, com cache entre invocações quentes ---------- */
type Meta = {
  rotulos: Map<string, Map<string, string>>;
  usuarios: Map<number, string>;
  etapas: Map<number, { nome: string; pipeline: number }>;
  funis: Map<number, string>;
  precos: Map<string, number>;
  buddyKey: string | null;   // campo do time de CS, descoberto pelo nome
  em: number;
};
let META: Meta | null = null;
const META_TTL = 10 * 60_000;

async function meta(): Promise<Meta> {
  if (META && Date.now() - META.em < META_TTL) return META;

  const rotulos = new Map<string, Map<string, string>>();
  // limit=500: sem isso a API devolve só os 100 primeiros campos e metade dos
  // rótulos some — foi o que fez "Produto" e "Temperatura" virarem nulo.
  const campos = await pd("/api/v1/dealFields?start=0&limit=500");
  for (const f of campos.data ?? []) {
    if (!f.options?.length) continue;
    const m = new Map<string, string>();
    for (const o of f.options) m.set(String(o.id), o.label);
    rotulos.set(f.key, m);
  }

  // O campo do time de CS ("Buddy") não tem chave fixa combinada — em vez de
  // chumbar um hash que pode mudar, procuramos pelo nome e, se não achar,
  // pelo campo cujas opções contêm o time. Assim ninguém precisa mexer no código
  // quando alguém renomear a coluna no Pipedrive.
  const TIME_CS = ["allana", "castagne", "robert", "aline", "andrea"];
  let buddyKey: string | null = null;
  for (const f of campos.data ?? []) {
    if (/buddy|customer\s*success|\bcs\b/i.test(String(f.name ?? ""))) { buddyKey = f.key; break; }
  }
  if (!buddyKey) {
    for (const f of campos.data ?? []) {
      const nomes = (f.options ?? []).map((o: any) => String(o.label ?? "").toLowerCase());
      if (nomes.length && TIME_CS.filter((x) => nomes.some((n) => n.includes(x))).length >= 2) {
        buddyKey = f.key; break;
      }
    }
  }

  const usuarios = new Map<number, string>();
  for (let start = 0; ; start += 500) {
    const r = await pd(`/api/v1/users?start=${start}&limit=500`);
    for (const u of r.data ?? []) usuarios.set(u.id, u.name);
    if (!r.additional_data?.pagination?.more_items_in_collection) break;
  }

  const etapas = new Map<number, { nome: string; pipeline: number }>();
  const st = await pd("/api/v1/stages?limit=500");
  for (const s of st.data ?? []) etapas.set(s.id, { nome: s.name, pipeline: s.pipeline_id });

  const funis = new Map<number, string>();
  const pl = await pd("/api/v1/pipelines?limit=500");
  for (const p of pl.data ?? []) funis.set(p.id, p.name);

  const precos = new Map<string, number>();
  for (let start = 0; ; start += 500) {
    const r = await pd(`/api/v1/products?start=${start}&limit=500`);
    for (const p of r.data ?? []) {
      const brl = (p.prices ?? []).find((x: any) => x.currency === "BRL") ?? (p.prices ?? [])[0];
      if (p.name && brl?.price) precos.set(chave(p.name), Number(brl.price));
    }
    if (!r.additional_data?.pagination?.more_items_in_collection) break;
  }

  META = { rotulos, usuarios, etapas, funis, precos, buddyKey, em: Date.now() };
  return META;
}

const chave = (s: unknown) =>
  String(s ?? "").toLowerCase().normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "");

/* ---------- leitura de campos ---------- */
const cru = (v: any) => (v && typeof v === "object" ? (v.id ?? v.value ?? null) : (v ?? null));
const num = (v: any): number | null => {
  if (v === null || v === undefined || v === "") return null;
  if (typeof v === "object") return num(v.value ?? v.amount ?? null);
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};
const dia = (v: any) => (typeof v === "string" && v.length >= 10 ? v.slice(0, 10) : null);
const adiante = (iso: string, n: number) =>
  new Date(Date.parse(iso + "T12:00:00Z") + n * 86400000).toISOString().slice(0, 10);
const cf = (d: any, h: string) => d?.custom_fields?.[h] ?? d?.[h] ?? null;

function rot(m: Meta, campo: string, v: any): string | null {
  const b = cru(v);
  if (b === null || b === undefined || b === "") return null;
  const achado = m.rotulos.get(campo)?.get(String(b));
  if (achado) return achado;
  // enum sem opção conhecida vira null; texto livre continua sendo o próprio texto
  return typeof b === "string" && !/^\d+$/.test(b) ? b : null;
}
function rotLista(m: Meta, campo: string, v: any): string[] {
  if (v === null || v === undefined || v === "") return [];
  const arr = Array.isArray(v) ? v : String(v).split(",");
  return arr.map((x) => rot(m, campo, typeof x === "string" ? x.trim() : x)).filter(Boolean) as string[];
}
function usuario(m: Meta, v: any): { id: number | null; nome: string | null } {
  const id = num(cru(v));
  return { id, nome: id != null ? (m.usuarios.get(id) ?? null) : null };
}

/* ---------- busca dos negócios ---------- */
// Ganhos e criados: a timeline filtra por data no próprio servidor do Pipedrive,
// no campo que a gente escolher. É o mesmo critério do card [AE] Ganhos
// ("Ganho em" = won_time), e foi o que fez os números baterem.
async function porData(campo: "won_time" | "add_time", de: string, dias: number) {
  const q = new URLSearchParams({
    start_date: de, interval: "day", amount: String(dias),
    field_key: campo, exclude_deleted_deals: "1",
  });
  const r = await pd(`/api/v1/deals/timeline?${q}`);
  return (r.data ?? []).flatMap((p: any) => p.deals ?? []);
}

// Perdidos: a timeline não devolve nada para lost_time — por isso o painel
// mostrava Lost = 0. Aqui vai por status, e o corte de data é feito na volta.
// Perder um negócio mexe no update_time, então updated_since não deixa passar nada.
function perdidos(de: string, ate: string) {
  const noPeriodo = (d: any) => {
    const x = dia(d.lost_time);
    return !!x && x >= de && x <= ate;
  };
  return paginaV2("lost", { updated_since: de + "T00:00:00Z" }, noPeriodo);
}

// Carteira aberta. Só interessa negócio com "Vendedor" preenchido.
// NÃO usar updated_since aqui: foi tentado e derrubou a carteira de 124 para 37.
function abertos() {
  const temVendedor = (d: any) => cru(cf(d, CAMPOS.vendedor)) != null;
  return paginaV2("open", {}, temVendedor);
}

// Histórico de churn dos últimos 12 meses, independente do período do topo.
// O cancelamento é um campo customizado — não dá para filtrar por ele no servidor.
// Então buscamos os GANHOS de 12 meses (é de onde todo churn sai) e guardamos só
// os que cancelaram, já reduzidos ao mínimo: o negócio inteiro na memória por um
// ano de vendas foi o que estourou a função da primeira vez.
async function historicoChurn(m: Meta, ate: string) {
  const fim = new Date(Date.parse(ate + "T12:00:00Z"));
  const linhas: any[] = [];
  // A meta de churn da casa é sobre o RECEBIMENTO, não sobre a contagem de alunos.
  // Como já estamos varrendo todos os ganhos de 12 meses, o total recebido por mês
  // sai de graça aqui — sem ele o gráfico não teria denominador.
  const meses = new Map<string, { ganhos: number; valor: number; recebido: number }>();
  // em blocos de 3 meses: 4 respostas pequenas em vez de uma gigante
  for (let bloco = 3; bloco >= 0; bloco--) {
    const ini = new Date(fim);
    ini.setUTCMonth(ini.getUTCMonth() - (bloco + 1) * 3 + 1);
    ini.setUTCDate(1);
    const de = ini.toISOString().slice(0, 10);
    let brutos: any[] = [];
    try {
      const q = new URLSearchParams({
        start_date: de, interval: "month", amount: "3",
        field_key: "won_time", exclude_deleted_deals: "1",
      });
      const r = await pd(`/api/v1/deals/timeline?${q}`);
      brutos = (r.data ?? []).flatMap((x: any) => x.deals ?? []);
    } catch { continue; }

    for (const d of brutos) {
      const mesGanho = (dia(d.won_time) ?? "").slice(0, 7);
      if (mesGanho) {
        const acc = meses.get(mesGanho) ?? { ganhos: 0, valor: 0, recebido: 0 };
        acc.ganhos++;
        acc.valor += num(d.value) ?? 0;
        // Valor pago é o que de fato entrou; quando ninguém preencheu, o valor do
        // negócio é a melhor aproximação — e o painel diz na tela quando isso acontece.
        acc.recebido += num(cf(d, CAMPOS.valorPago)) || (num(d.value) ?? 0);
        meses.set(mesGanho, acc);
      }

      const dtCancel = dia(cf(d, CAMPOS.dtCancel));
      const saude = rot(m, CAMPOS.saude, cf(d, CAMPOS.saude));
      if (saude !== "Cancelado" && !dtCancel) continue;
      const vend = usuario(m, cf(d, CAMPOS.vendedor));
      const contratado = rot(m, CAMPOS.produto, cf(d, CAMPOS.produto));
      linhas.push({
        id: d.id,
        t: d.title ?? "(sem título)",
        v: vend.nome ?? "Sem vendedor",
        p: contratado ?? rot(m, CAMPOS.apresentado, cf(d, CAMPOS.apresentado)) ?? "Sem produto",
        buddy: buddyDe(m, d),
        val: num(d.value) ?? 0,
        valPago: num(cf(d, CAMPOS.valorPago)) ?? 0,
        reemb: num(cf(d, CAMPOS.reembolso)) ?? 0,
        dGanho: dia(d.won_time),
        dc: dtCancel,
        saude,
        cm: rotLista(m, CAMPOS.motivoChurn, cf(d, CAMPOS.motivoChurn)),
      });
    }
    brutos.length = 0;
  }
  // o mesmo negócio não pode aparecer duas vezes se os blocos se encostarem
  const vistos = new Set<number>();
  return {
    linhas: linhas.filter((x) => !vistos.has(x.id) && vistos.add(x.id)),
    meses: [...meses.entries()].sort().map(([mes, x]) => ({ mes, ...x })),
  };
}

/* Onde a reunião aconteceu de verdade.
   O campo "Canal de Conexão" do negócio só tem as opções que alguém cadastrou —
   Google Meet não está lá. Mas a ATIVIDADE do Pipedrive guarda a plataforma da
   videochamada em conference_meeting_client ("google_meet", "zoom", "teams") e o
   link em conference_meeting_url. É o único jeito de saber isso olhando para trás,
   sem depender de o time passar a preencher um campo novo.

   Só vale para reunião criada pela integração de vídeo do Pipedrive; reunião
   marcada por fora entra como atividade comum e cai em "outro". */
const PLATAFORMAS: Array<[string, RegExp]> = [
  ["Google Meet", /google_?meet|meet\.google\.com/i],
  ["Zoom",        /zoom/i],
  ["Teams",       /teams|microsoft/i],
  ["Meetime",     /meetime/i],
  ["Whereby",     /whereby/i],
];

function plataformaDa(a: any): string | null {
  const pistas = [a.conference_meeting_client, a.conference_meeting_url,
                  a.location, a.subject, a.note].filter(Boolean).join(" ");
  for (const [nome, re] of PLATAFORMAS) if (re.test(pistas)) return nome;
  if (a.type === "call") return "Ligação";
  return null;
}

async function atividades(de: string, ate: string, hoje: string, interesse: Set<number>) {
  type Acc = {
    plataformas: Record<string, number>; reunioes: number;
    proxima: string | null; proximaAssunto: string | null; proximaEhReuniao: boolean;
  };
  const porNegocio = new Map<number, Acc>();
  const total: Record<string, number> = {};
  // O que o Pipedrive realmente devolve, sem interpretação nossa: serve para
  // descobrir por que uma plataforma não aparece, em vez de ficar no chute.
  const clientes: Record<string, number> = {};
  const hosts: Record<string, number> = {};
  const tipos: Record<string, number> = {};
  let vistas = 0, comLink = 0, truncado = false;

  for (let pagina = 0; pagina < 12; pagina++) {
    // Sem done=1: reunião que aconteceu mas ninguém marcou como concluída também
    // conta — era isso que estava escondendo metade das reuniões.
    const q = new URLSearchParams({
      start_date: de, end_date: ate, user_id: "0",
      start: String(pagina * 500), limit: "500",
    });
    let r: any;
    try { r = await pd(`/api/v1/activities?${q}`); }
    catch { truncado = true; break; }

    const lote = r.data ?? [];
    for (const a of lote) {
      const id = Number(a.deal_id);
      if (!id || !interesse.has(id)) continue;
      vistas++;
      tipos[String(a.type ?? "?")] = (tipos[String(a.type ?? "?")] ?? 0) + 1;
      if (a.conference_meeting_client) {
        const c = String(a.conference_meeting_client);
        clientes[c] = (clientes[c] ?? 0) + 1;
      }
      if (a.conference_meeting_url) {
        comLink++;
        try {
          const h = new URL(String(a.conference_meeting_url)).hostname;
          hosts[h] = (hosts[h] ?? 0) + 1;
        } catch { /* url torta não ajuda nem atrapalha */ }
      }
      const plat = plataformaDa(a);
      if (!plat) continue;
      total[plat] = (total[plat] ?? 0) + 1;
      const acc = porNegocio.get(id) ??
        { plataformas: {}, reunioes: 0, proxima: null, proximaAssunto: null,
          proximaEhReuniao: false };
      acc.plataformas[plat] = (acc.plataformas[plat] ?? 0) + 1;
      acc.reunioes++;
      porNegocio.set(id, acc);
    }
    lote.length = 0;
    if (!r.additional_data?.pagination?.more_items_in_collection) break;
    if (pagina === 11) truncado = true;
  }
  /* SEGUNDA varredura, separada de propósito.
     ==========================================
     A agenda futura é outra pergunta: "quando é o próximo retorno". Ela poderia
     ter entrado no laço acima esticando o end_date — e foi o que eu fiz primeiro.
     É armadilha: aquele laço tem teto de 12 páginas, e enfiar 90 dias a mais no
     mesmo orçamento faz ele estourar e passar a perder atividade PASSADA, que é
     o que alimenta o funil e as plataformas. Um número que estava certo viraria
     errado por causa de uma pergunta nova.

     Separada, a busca de cima continua byte a byte o que era. Esta é pequena:
     `done=0` corta tudo que já foi concluído, e a janela começa hoje. */
  for (let pagina = 0; pagina < 8; pagina++) {
    const q = new URLSearchParams({
      start_date: hoje, end_date: adiante(hoje, 90), done: "0", user_id: "0",
      start: String(pagina * 500), limit: "500",
    });
    let r: any;
    try { r = await pd(`/api/v1/activities?${q}`); }
    catch { truncado = true; break; }

    for (const a of r.data ?? []) {
      const id = Number(a.deal_id);
      if (!id || !interesse.has(id)) continue;
      const venc = dia(a.due_date);
      if (!venc || venc < hoje) continue;
      const acc = porNegocio.get(id) ??
        { plataformas: {}, reunioes: 0, proxima: null, proximaAssunto: null,
          proximaEhReuniao: false };
      const cand: Escolha = { quando: venc, assunto: a.subject ?? null, ehReuniao: ehReuniao(a) };
      const atual: Escolha | null = acc.proxima
        ? { quando: acc.proxima, assunto: acc.proximaAssunto, ehReuniao: acc.proximaEhReuniao }
        : null;
      if (melhorQue(atual, cand)) {
        acc.proxima = cand.quando;
        acc.proximaAssunto = cand.assunto;
        acc.proximaEhReuniao = cand.ehReuniao;
      }
      porNegocio.set(id, acc);
    }
    if (!r.additional_data?.pagination?.more_items_in_collection) break;
  }

  return { porNegocio, total, vistas, comLink, clientes, hosts, tipos, truncado };
}

// Itens do negócio: preço praticado x preço de tabela. Só para os ganhos.
async function itensDosGanhos(ids: number[]) {
  const mapa = new Map<number, any[]>();
  for (let i = 0; i < ids.length; i += 5) {
    const rs = await Promise.all(ids.slice(i, i + 5).map(async (id) => {
      try { return [id, (await pd(`/api/v1/deals/${id}/products?limit=100`)).data ?? []] as const; }
      catch { return [id, []] as const; }
    }));
    for (const [id, itens] of rs) mapa.set(id, itens as any[]);
    if (i + 5 < ids.length) await pausa(100);
  }
  return mapa;
}

/* ---------- análise da call ----------
   Não existe tabela nem campo: a análise é uma ANOTAÇÃO no negócio, escrita
   pela "IA ICOMM (API)" num formato fixo. Puxamos as anotações da janela e
   lemos o texto. A âncora é o rodapé "icomm-call-analysis" (ou o título). */
const ANCORA = /icomm-call-analysis|AN[ÁA]LISE DA CALL/i;

// Devolve já o mapa deal_id -> análise. O texto da anotação é lido e descartado
// no mesmo passo: guardar as notas cruas era o que pesava na memória.
async function anotacoes(de: string, ate: string) {
  const mapa = new Map<number, any>();
  // a análise costuma ser escrita perto da call, mas o negócio pode fechar
  // depois — por isso a janela das notas começa antes do período.
  const desde = new Date(Date.parse(de) - 60 * 86400000).toISOString().slice(0, 10);
  for (let pagina = 0; pagina < 12; pagina++) {
    const q = new URLSearchParams({
      start: String(pagina * 100), limit: "100",
      start_date: desde, end_date: ate, sort: "add_time DESC",
    });
    const r = await pd(`/api/v1/notes?${q}`);
    for (const n of r.data ?? []) {
      if (!n.deal_id || !ANCORA.test(String(n.content ?? ""))) continue;
      const a = lerAnalise(n);
      if (!a) continue;
      const antes = mapa.get(a.deal_id);
      // se houver mais de uma análise no mesmo negócio, fica a mais recente
      if (!antes || String(a.em) > String(antes.em)) mapa.set(a.deal_id, a);
    }
    if (!r.additional_data?.pagination?.more_items_in_collection) break;
  }
  return mapa;
}

// A anotação vem como HTML. Vira texto puro, preservando as quebras.
function texto(html: string) {
  return String(html ?? "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/(p|div|li|h\d)>/gi, "\n")
    .replace(/<li[^>]*>/gi, "• ")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
}

const TITULOS = [
  "Resumo", "O que deu certo", "O que deu errado", "Como deveria ter conduzido",
  "Por que não fechou", "Por que fechou", "Como chegamos na nota",
];
// Recorta o texto nos títulos conhecidos. Cada seção vai do seu título até o próximo.
function secoes(txt: string) {
  const linhas = txt.split("\n");
  const achadas: Record<string, string[]> = {};
  let atual: string | null = null;
  for (const linha of linhas) {
    const limpa = linha.trim();
    const titulo = TITULOS.find((t) => limpa.toLowerCase() === t.toLowerCase()
      || limpa.toLowerCase().startsWith(t.toLowerCase() + " —")
      || limpa.toLowerCase().startsWith(t.toLowerCase() + ":"));
    if (titulo) { atual = titulo; achadas[titulo] ??= []; continue; }
    if (atual && limpa) achadas[atual].push(limpa);
  }
  return achadas;
}
const bullets = (linhas: string[] | undefined) =>
  (linhas ?? []).filter((l) => /^[•\-\*]/.test(l)).map((l) => l.replace(/^[•\-\*]\s*/, "").trim())
    .filter(Boolean);
const paragrafo = (linhas: string[] | undefined) =>
  (linhas ?? []).filter((l) => !/^[•\-\*]/.test(l)).join(" ").trim() || null;

function lerAnalise(nota: any) {
  const txt = texto(nota.content);
  const pega = (re: RegExp) => txt.match(re)?.[1]?.trim() ?? null;

  const nota10 = pega(/Nota\s+geral:\s*([\d.,]+)\s*\/\s*10/i);
  if (!nota10) return null;                      // sem nota não é análise utilizável

  const s = secoes(txt);
  const certo = bullets(s["O que deu certo"]);
  const erro = bullets(s["O que deu errado"]);
  const cond = bullets(s["Como deveria ter conduzido"]);
  const porque = paragrafo(s["Por que não fechou"]) ?? paragrafo(s["Por que fechou"]);
  const resumo = paragrafo(s["Resumo"]);

  return {
    deal_id: nota.deal_id,
    nota: Number(nota10.replace(",", ".")),
    dur: Number(pega(/Dura[çc][ãa]o:\s*(\d+)\s*min/i) ?? 0) || null,
    cp: Number(pega(/closer\s*~?\s*(\d+)\s*%/i) ?? 0) || null,
    lp: Number(pega(/lead\s*~?\s*(\d+)\s*%/i) ?? 0) || null,
    closer: pega(/Closer:\s*([^|\n]+)/i),
    sdrNota: pega(/SDR:\s*([^|\n]+)/i),
    codigo: pega(/C[óo]digo:\s*([^\s|]+)/i),
    valorPitch: (() => {
      const v = pega(/Valor ofertado no pitch:[^R]*R\$\s*([\d.,]+)/i);
      return v ? Number(v.replace(/\./g, "").replace(",", ".")) : null;
    })(),
    parc: Number(pega(/em\s*(\d+)x/i) ?? 0) || null,
    resumo, certo, erro, cond, porque,
    nota_justificativa: pega(/Nota\s+geral:\s*[\d.,]+\s*\/\s*10\s*[—-]\s*([^\n]+)/i),
    em: nota.add_time ?? null,
    texto_erro: [erro.join(" "), porque ?? ""].join(" "),
  };
}

/* ---------- objeções ----------
   Saem de dois lugares, e ficam marcadas com a origem para não misturar
   "o closer errou" com "o lead disse não por X". */
const GATILHOS: Array<[string, RegExp]> = [
  ["Sem caixa",           /sem caixa|caixa (curto|apertado|horr[íi]vel)|desafio de caixa|sem or[çc]amento|n[ãa]o qualificou caixa/i],
  ["Decisor ausente",     /decisor|s[óo]cio n[ãa]o (estava|participou)|sem o s[óo]cio|executores fora|quem decide n[ãa]o/i],
  ["Não vê valor",        /n[ãa]o v[êe] valor|n[ãa]o construiu valor|n[ãa]o percebeu valor|valor n[ãa]o ficou claro/i],
  ["Forma de pagamento",  /parcelament|forma de pagamento|boleto|cart[ãa]o em \d+x|sem juros|n[ãa]o cabia/i],
  ["Momento errado",      /outro momento|momento errado|mais pra frente|ano que vem|sem urg[êe]ncia|prazo interno/i],
  ["Concorrente",         /concorrent|outra empresa|outra consultoria|comparou pre[çc]o/i],
  ["Super-promessa",      /super-?promessa|prometeu (venda|resultado)|promessa (irreal|sem lastro)/i],
  ["Desconto antecipado", /desconto (no primeiro minuto|antes|antecipad)|sinalizou desconto|concess[ãa]o sem contrapartida/i],
  ["Monólogo",            /mon[óo]logo|falou \d{2}% do tempo|closer ~?[89]\d%/i],
];
function objecoes(an: any, motivoPerda: string | null) {
  const saida: Array<{ nome: string; origem: "call" | "perda" }> = [];
  if (an?.texto_erro) {
    for (const [nome, re] of GATILHOS) {
      if (re.test(an.texto_erro)) saida.push({ nome, origem: "call" });
    }
  }
  if (motivoPerda) saida.push({ nome: motivoPerda, origem: "perda" });
  return saida;
}

/* ---------- preço de tabela ----------
   Quase nenhum negócio tem produto anexado como item; o time usa só o campo
   "Produto". Então o preço vem do catálogo, casando pelo nome. Casa exato,
   depois por prefixo — e o que não casar é reportado, para arrumar o catálogo. */
const semPreco = new Set<string>();
function precoDeTabela(m: Meta, nomeProduto: string, itens: any[] | undefined) {
  if (itens?.length) {
    return itens.reduce((a, i) => a + Number(i.item_price ?? 0) * Number(i.quantity ?? 1), 0);
  }
  const k = chave(nomeProduto);
  if (!k) return 0;
  const exato = m.precos.get(k);
  if (exato) return exato;
  for (const [nome, valor] of m.precos) {
    if (nome.startsWith(k) || k.startsWith(nome)) return valor;
  }
  if (nomeProduto && nomeProduto !== "Sem produto") semPreco.add(nomeProduto);
  return 0;
}

/* O campo de CS pode ser lista de opções ou pessoa do Pipedrive — tentamos as duas
   leituras antes de desistir. */
function buddyDe(m: Meta, d: any) {
  if (!m.buddyKey) return null;
  const bruto = cf(d, m.buddyKey);
  if (bruto == null) return null;
  const texto = String(cru(bruto) ?? "").trim();
  return rot(m, m.buddyKey, bruto) ?? usuario(m, bruto).nome ?? (texto || null);
}

/* ---------- normalização ---------- */
function mapear(m: Meta, d: any, itens: any[] | undefined, an: any, hoje: string) {
  const status: "won" | "lost" | "open" =
    d.status === "won" ? "won" : d.status === "lost" ? "lost" : "open";

  // "Produto" só é preenchido no fechamento. Aberto e perdido caem para o
  // apresentado e depois para o sugerido — senão quase tudo vira "Sem produto".
  const contratado = rot(m, CAMPOS.produto, cf(d, CAMPOS.produto));
  const apresentado = rot(m, CAMPOS.apresentado, cf(d, CAMPOS.apresentado));
  const sugerido = rot(m, CAMPOS.sugerido, cf(d, CAMPOS.sugerido));
  const p = contratado ?? apresentado ?? sugerido ?? "Sem produto";
  const pFonte = contratado ? "contratado" : apresentado ? "apresentado" : sugerido ? "sugerido" : null;

  const vend = usuario(m, cf(d, CAMPOS.vendedor));
  const et = m.etapas.get(Number(cru(d.stage_id)));

  const dCriacao = dia(d.add_time);
  const dGanho = dia(d.won_time);
  const dPerda = dia(d.lost_time);
  const dDesfecho = dGanho ?? dPerda ?? dia(d.close_time) ?? dCriacao;
  const paradoDesde = dia(d.stage_change_time) ?? dia(d.update_time) ?? dCriacao;

  const dtCancel = dia(cf(d, CAMPOS.dtCancel));
  const saude = rot(m, CAMPOS.saude, cf(d, CAMPOS.saude));
  const motivoPerda = rot(m, "lost_reason", d.lost_reason) ?? (d.lost_reason || null);

  return {
    id: d.id,
    t: d.title ?? "(sem título)",
    v: vend.nome ?? "Sem vendedor",
    vid: vend.id,
    dono: usuario(m, d.user_id ?? d.owner_id).nome,
    p, pFonte,
    s: status,
    val: num(d.value) ?? 0,
    valPago: num(cf(d, CAMPOS.valorPago)) ?? 0,
    dCriacao, dGanho, dPerda, dDesfecho,
    funil: m.funis.get(Number(cru(d.pipeline_id))) ?? null,
    et: et?.nome ?? "Sem etapa",
    tmp: rot(m, CAMPOS.temperatura, cf(d, CAMPOS.temperatura)),
    lead: rot(m, CAMPOS.lead, cf(d, CAMPOS.lead)),
    leadSql: rot(m, CAMPOS.leadSql, cf(d, CAMPOS.leadSql)),
    sug: sugerido, ofe: apresentado,
    canal: rot(m, CAMPOS.canalConex, cf(d, CAMPOS.canalConex))
        ?? rot(m, CAMPOS.canalQualif, cf(d, CAMPOS.canalQualif)),
    orig: rot(m, CAMPOS.origemContr, cf(d, CAMPOS.origemContr)),
    bu: rot(m, CAMPOS.bu, cf(d, CAMPOS.bu)),
    sdr: usuario(m, cf(d, CAMPOS.sdr)).nome,
    buddy: buddyDe(m, d),
    obs: cf(d, CAMPOS.obsCall) ?? null,
    lm: motivoPerda,
    ld: cf(d, CAMPOS.descPerda) ?? null,
    lt: dPerda,
    saude,
    churn: saude === "Cancelado" || !!dtCancel,
    cm: rotLista(m, CAMPOS.motivoChurn, cf(d, CAMPOS.motivoChurn)),
    reemb: num(cf(d, CAMPOS.reembolso)) ?? 0,
    dc: dtCancel,
    nret: num(cf(d, CAMPOS.nroRetornos)),
    retAgendado: dia(cf(d, CAMPOS.retAgendado)),
    retRealizado: dia(cf(d, CAMPOS.retRealizado)),
    noShow: dia(cf(d, CAMPOS.noShow)),
    diaReuniao: dia(cf(d, CAMPOS.diaReuniao)),
    diaOpp: dia(cf(d, CAMPOS.diaOpp)),
    /* SAL = Sales Accepted Lead: o dia em que o CLOSER aceitou o lead. Estava
       declarado em CAMPOS desde sempre e o mapear() nunca lia, então nunca
       chegou na tela. Serve para separar o ciclo do closer do ciclo do SDR:
       "criação → ganho" mistura o tempo dos dois; "SAL → ganho" é só o dele. */
    dSal: dia(cf(d, CAMPOS.dataSal)),
    dSql: dia(cf(d, CAMPOS.dataSql)),
    precoLista: precoDeTabela(m, p, itens),
    itens: (itens ?? []).map((i) => ({
      nome: i.name ?? i.product?.name ?? null,
      qtd: Number(i.quantity ?? 1), preco: Number(i.item_price ?? 0),
    })),
    an: an ?? null,
    obj: objecoes(an, motivoPerda),
    dpar: status === "open" && paradoDesde
      ? Math.round((Date.parse(hoje + "T12:00:00Z") - Date.parse(paradoDesde + "T12:00:00Z")) / 86400000)
      : null,
  };
}

/* ---------- handler ---------- */
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  const t0 = Date.now();
  try {
    if (!PD_TOKEN) throw new Error("Falta o secret PIPEDRIVE_API_TOKEN");
    semPreco.clear();
    truncou.clear();
    for (const k of Object.keys(DIAG_V2)) delete DIAG_V2[k];

    const url = new URL(req.url);
    const hoje = new Date().toISOString().slice(0, 10);
    const ate = url.searchParams.get("ate") ?? hoje;
    const de = url.searchParams.get("de") ??
      new Date(Date.parse(ate) - 29 * 86400000).toISOString().slice(0, 10);
    if (de > ate) throw new Error("Período invertido: 'de' é maior que 'ate'");
    const dias = Math.min(400, Math.floor((Date.parse(ate) - Date.parse(de)) / 86400000) + 1);

    const m = await meta();
    const [ganhos, criados, lost, emAberto, analises, churn12] = await Promise.all([
      porData("won_time", de, dias),
      porData("add_time", de, dias),
      perdidos(de, ate),
      abertos(),
      anotacoes(de, ate),
      historicoChurn(m, ate),
    ]);

    const dentro = (v: any) => { const x = dia(v); return !!x && x >= de && x <= ate; };
    const bruto = new Map<number, any>();
    for (const d of ganhos)   if (dentro(d.won_time))  bruto.set(d.id, d);
    for (const d of lost)     if (dentro(d.lost_time)) bruto.set(d.id, d);
    for (const d of criados)  if (dentro(d.add_time))  bruto.set(d.id, d);
    for (const d of emAberto) if (!bruto.has(d.id))    bruto.set(d.id, d);

    const idsGanhos = [...bruto.values()]
      .filter((d) => d.status === "won" && dentro(d.won_time)).map((d) => d.id);
    const idsTodos = new Set<number>([...bruto.keys()]);
    const [itens, ativ] = await Promise.all([
      itensDosGanhos(idsGanhos),
      atividades(de, ate, hoje, idsTodos),
    ]);

    const todos = [...bruto.values()]
      .map((d) => {
        const x = mapear(m, d, itens.get(d.id), analises.get(d.id), hoje);
        const a = ativ.porNegocio.get(d.id);
        // a plataforma mais usada no negócio é a que representa a reunião
        const top = a && Object.entries(a.plataformas).sort((p, q) => q[1] - p[1])[0];

        /* `retAgendado` passa a significar QUANDO O RETORNO É, e não "o que
           está escrito no campo". Quando existe atividade em aberto, é ela que
           manda: o campo não acompanha remarcação.

           Só para negócio ABERTO. Em ganho e perdido o campo é registro
           histórico e mexer nele mudaria `veioDeRet`, que decide se a venda
           saiu de um retorno.

           O valor cru do campo continua saindo em `retCampo`, para dar para
           medir a diferença sem adivinhar. */
        const proxima = x.s === "open" ? (a?.proxima ?? null) : null;
        return {
          ...x,
          retCampo: x.retAgendado,
          retAgendado: proxima ?? x.retAgendado,
          retFonte: proxima ? "atividade" : x.retAgendado ? "campo" : null,
          retAssunto: proxima ? (a?.proximaAssunto ?? null) : null,
          plataforma: top ? top[0] : null,
          reunioesAtiv: a?.reunioes ?? 0,
        };
      });

    // Só entra negócio com o campo "Vendedor" preenchido — é o mesmo critério
    // dos cards [AE] do Insights. Sem isso, a carteira aberta da conta inteira
    // (outros funis, outros times) entrava como "Sem vendedor".
    const deals = todos.filter((d) => d.vid != null);
    const foraSemVendedor = todos.length - deals.length;

    // Conferência com o card [AE] Ganhos: won + won_time no período, por Vendedor.
    const noPeriodo = deals.filter((d) => d.s === "won" && dentro(d.dGanho));
    const porVendedor: Record<string, { negocios: number; valor: number }> = {};
    for (const d of noPeriodo) {
      porVendedor[d.v] ??= { negocios: 0, valor: 0 };
      porVendedor[d.v].negocios++;
      porVendedor[d.v].valor += d.val;
    }

    // Quanto do que "é pra preencher" está de fato preenchido. Serve para cobrar
    // o time com número, e para a gente saber em qual campo dá para confiar.
    const emAberto2 = deals.filter((d) => d.s === "open");
    const pct = (n: number, t: number) => (t ? Math.round((n / t) * 100) : 0);
    const preenchimento = {
      base_abertos: emAberto2.length,
      // de propósito sobre `retCampo`: é o preenchimento do CAMPO que se quer
      // medir. Contra `retAgendado` isto viraria quase 100% e esconderia que
      // ninguém preenche — que é justamente o que se está cobrando.
      retorno_agendado: pct(emAberto2.filter((d) => d.retCampo).length, emAberto2.length),
      retorno_realizado: pct(emAberto2.filter((d) => d.retRealizado).length, emAberto2.length),
      no_show: pct(emAberto2.filter((d) => d.noShow).length, emAberto2.length),
      dia_reuniao: pct(emAberto2.filter((d) => d.diaReuniao).length, emAberto2.length),
      canal: pct(emAberto2.filter((d) => d.canal).length, emAberto2.length),
      temperatura: pct(emAberto2.filter((d) => d.tmp).length, emAberto2.length),
      nro_retornos: pct(emAberto2.filter((d) => d.nret != null).length, emAberto2.length),
    };

    const avisos: string[] = [];
    if (foraSemVendedor) avisos.push(
      `${foraSemVendedor} negócio(s) ficaram de fora por estarem <b>sem o campo "Vendedor"</b> ` +
      `— mesmo critério dos cards [AE] do Insights.`);
    if (semPreco.size) avisos.push(
      `Sem preço de tabela no catálogo para: ${[...semPreco].map((x) => `<code>${x}</code>`).join(", ")} ` +
      `— cadastrar em Produtos no Pipedrive com o mesmo nome resolve as colunas Preço lista e Desc.`);
    if (!analises.size) avisos.push(
      `Nenhuma anotação de análise de call encontrada na janela — Score e resumo ficam vazios.`);
    if (!ativ.total["Google Meet"]) {
      const cli = Object.entries(ativ.clientes).map(([k, n]) => `${k} (${n})`).join(", ");
      const dom = Object.entries(ativ.hosts).map(([k, n]) => `${k} (${n})`).join(", ");
      avisos.push(
        `Nenhuma reunião de <b>Google Meet</b> identificada. ` +
        (cli ? `Plataformas de vídeo encontradas: ${cli}. ` : `Nenhuma atividade traz plataforma de vídeo. `) +
        (dom ? `Domínios dos links: ${dom}. ` : "") +
        `O Meet só é gravado quando a reunião é criada pela integração de vídeo do Pipedrive.`);
    }
    if (ativ.truncado) avisos.push(
      `A varredura de <b>atividades</b> bateu no teto de páginas — pode faltar reunião antiga.`);
    if (!m.buddyKey) avisos.push(
      `Não encontrei o campo do time de CS (Buddy) no Pipedrive — o corte por Buddy ` +
      `na página Churn fica vazio. Procurei por nome ("Buddy", "CS", "Customer Success") ` +
      `e pelas opções do campo.`);
    if (truncou.size) avisos.push(
      `A varredura de <b>${[...truncou].join(" e ")}</b> bateu no teto de páginas — ` +
`faltou negócio antigo.`);

    return Response.json({
      ok: true,
      periodo: { de, ate, dias },
      geradoEm: new Date().toISOString(),
      ms: Date.now() - t0,
      conferencia: {
        ae_ganhos: {
          negocios: noPeriodo.length,
          valor: noPeriodo.reduce((a, d) => a + d.val, 0),
          por_vendedor: porVendedor,
        },
      },
      preenchimento,
      /* Campo × agenda: em quantos negócios abertos os dois discordam. Se der
         quase zero, o campo estava bom e a troca foi inócua; se der alto, é a
         medida do estrago que o campo desatualizado vinha fazendo. */
      retorno_fonte: (() => {
        const c = { pela_atividade: 0, pelo_campo: 0, sem_nada: 0, discordam: 0 };
        for (const d of emAberto2) {
          if (d.retFonte === "atividade") c.pela_atividade++;
          else if (d.retFonte === "campo") c.pelo_campo++;
          else c.sem_nada++;
          if (d.retFonte === "atividade" && d.retCampo && d.retCampo !== d.retAgendado) c.discordam++;
        }
        return c;
      })(),
      // O que cada varredura leu de fato — é isto que responde "por que a
      // carteira aberta veio menor do que deveria".
      varredura: DIAG_V2,
      contagem: {
        total: deals.length,
        ganhos: deals.filter((d) => d.s === "won").length,
        perdidos: deals.filter((d) => d.s === "lost").length,
        abertos: deals.filter((d) => d.s === "open").length,
        com_analise: deals.filter((d) => d.an).length,
        fora_sem_vendedor: foraSemVendedor,
      },
      avisos,
      plataformas: {
        total: ativ.total,
        atividades_no_periodo: ativ.vistas,
        com_link_de_video: ativ.comLink,
        // cru, do Pipedrive: o que existe de fato no campo
        clientes_de_video: ativ.clientes,
        dominios_dos_links: ativ.hosts,
        tipos_de_atividade: ativ.tipos,
      },
      churn12: churn12.linhas,
      recebimento12: churn12.meses,
      deals,
    }, { headers: CORS });
  } catch (e) {
    return Response.json(
      { ok: false, erro: e instanceof Error ? e.message : String(e), ms: Date.now() - t0 },
      { status: 500, headers: CORS },
    );
  }
});

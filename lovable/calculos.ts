/* Contas do Painel Comercial ICOMM — sem tela, sem DOM, sem framework.
   ============================================================================
   Este arquivo é a ÚNICA fonte dos números. O painel antigo em HTML e a versão
   nova em React devem os dois chamar daqui.

   Por que existe: as regras abaixo parecem detalhe e não são. "Vencido" olha a
   data de referência e não hoje; a meta de churn é sobre recebimento e não
   sobre contagem de aluno; o forecast usa a conversão do próprio closer. Se
   alguém reescrever isso a partir de uma descrição em texto, os números saem
   diferentes E PARECENDO CERTOS — que é o pior defeito possível num painel de
   decisão. Importar este arquivo evita a reescrita.

   Não colocar nada de visual aqui. Formatação de moeda, cor e layout são da
   camada de cima.                                                             */

export type Analise = {
  nota: number; dur: number | null; cp: number | null; lp: number | null;
  resumo: string | null; certo: string[]; erro: string[]; cond: string[];
  porque: string | null;
};

export type Negocio = {
  id: number;
  t: string;                 // título do negócio
  v: string;                 // closer (campo "Vendedor")
  p: string;                 // produto
  s: "won" | "lost" | "open";
  val: number;               // valor do negócio
  valPago: number;           // o que de fato entrou
  et: string;                // etapa do funil
  tmp: string | null;        // Quente | Morno | Frio
  lead: string | null;       // A..F
  canal: string | null;
  orig: string | null;
  dCriacao: string | null;   // AAAA-MM-DD
  dGanho: string | null;
  dPerda: string | null;
  dDesfecho: string | null;
  dpar: number | null;       // dias parado na etapa
  nret: number | null;       // nº de retornos
  retAgendado: string | null;
  retRealizado: string | null;
  noShow: string | null;
  diaReuniao: string | null;
  churn: boolean;
  reemb: number;
  dc: string | null;         // data do cancelamento
  precoLista: number;
  an: Analise | null;
  [k: string]: unknown;
};

export type Filtros = {
  de: string;                // AAAA-MM-DD
  ate: string;
  basedata: "desfecho" | "criacao";
  orig?: string; vend?: string; prod?: string;
  canal?: string; lead?: string; temp?: string;
  /* "retorno" = só Retorno Agendado + Realizado; "followup" inclui Follow UP */
  ret?: "retorno" | "followup";
};

/* ---------- utilidades de data ---------- */
export const difDias = (a?: string | null, b?: string | null): number | null =>
  a && b ? Math.round((Date.parse(b + "T12:00:00Z") - Date.parse(a + "T12:00:00Z")) / 86400e3) : null;

export const maisDias = (iso: string, n: number): string =>
  new Date(Date.parse(iso + "T12:00:00Z") + n * 86400e3).toISOString().slice(0, 10);

/* ---------- recortes ---------- */
export const ETAPAS_RET = (f: Filtros): string[] =>
  f.ret === "followup"
    ? ["Retorno Agendado", "Retorno Realizado", "Follow UP"]
    : ["Retorno Agendado", "Retorno Realizado"];

/* Qual data manda no recorte do período. O padrão é o DESFECHO — é assim que o
   card [AE] do Insights do Pipedrive conta, e foi o que fez os números baterem. */
export const dataRef = (d: Negocio, f: Filtros): string | null =>
  f.basedata === "criacao" ? d.dCriacao : d.dDesfecho;

export const filtrosComuns = (d: Negocio, f: Filtros): boolean =>
  (!f.orig || d.orig === f.orig) &&
  (!f.vend || d.v === f.vend) &&
  (!f.prod || d.p === f.prod) &&
  (!f.canal || d.canal === f.canal) &&
  (!f.lead || d.lead === f.lead) &&
  (!f.temp || d.tmp === f.temp);

/** Negócios do período — é o que o Insights conta. */
export const base = (deals: Negocio[], f: Filtros): Negocio[] =>
  deals.filter(d => { const r = dataRef(d, f); return !!r && r >= f.de && r <= f.ate; })
       .filter(d => filtrosComuns(d, f));

/** Carteira aberta de hoje — NÃO depende do período, de propósito. */
export const carteira = (deals: Negocio[], f: Filtros): Negocio[] =>
  deals.filter(d => d.s === "open").filter(d => filtrosComuns(d, f));

/* ---------- agregados ---------- */
/* O que ainda pode virar receita: aberto com retorno agendado ou parado numa
   etapa de RET, projetado na conversão OBSERVADA do próprio recorte. Não é
   meta — é o que a régua atual entrega se nada mudar. */
function forecast(open: Negocio[], conv: number, f: Filtros) {
  const alvo = open.filter(d => d.retAgendado || ETAPAS_RET(f).includes(d.et));
  const fVal = alvo.reduce((a, d) => a + d.val, 0);
  return { fOpp: alvo.length, fVal, fConv: conv, fWon: alvo.length * conv, fRec: fVal * conv };
}

/** Quanto da receita ganha passou por retorno — é o que justifica a régua existir. */
function receitaRet(won: Negocio[], receita: number) {
  const r = won.filter(d => d.retAgendado || d.retRealizado || (d.nret ?? 0) > 0);
  const rec = r.reduce((a, d) => a + d.val, 0);
  return { retWon: r.length, retRec: rec, retPct: receita ? rec / receita : 0 };
}

/** Receita saída de negócio marcado como Quente — o teste da temperatura:
    se o quente não vende mais que o resto, o campo virou enfeite. */
function receitaQuente(won: Negocio[], receita: number) {
  const q = won.filter(d => d.tmp === "Quente");
  const rec = q.reduce((a, d) => a + d.val, 0);
  return { qWon: q.length, qRec: rec, qPct: receita ? rec / receita : 0 };
}

function cicloMedio(won: Negocio[]): number | null {
  const c = won.map(d => difDias(d.dCriacao, d.dGanho))
               .filter((x): x is number => x != null && x >= 0);
  return c.length ? c.reduce((a, b) => a + b, 0) / c.length : null;
}

export type Agregado = ReturnType<typeof agg>;

export function agg(rows: Negocio[], f: Filtros, ret?: Negocio[]) {
  const won = rows.filter(d => d.s === "won");
  const lost = rows.filter(d => d.s === "lost");
  const open = rows.filter(d => d.s === "open");
  const churn = rows.filter(d => d.churn);
  const emR = ret ?? open.filter(d => ETAPAS_RET(f).includes(d.et));
  const receita = won.reduce((a, d) => a + d.val, 0);
  const reemb = churn.reduce((a, d) => a + (d.reemb || 0), 0);
  const comNota = rows.filter(d => d.an);
  const lista = won.reduce((a, d) => a + (d.precoLista || 0), 0);
  const conv = rows.length ? won.length / rows.length : 0;
  return {
    opp: rows.length, won: won.length, lost: lost.length, ret: emR.length,
    outras: open.length - open.filter(d => ETAPAS_RET(f).includes(d.et)).length,
    q: emR.filter(d => d.tmp === "Quente").length,
    m: emR.filter(d => d.tmp === "Morno").length,
    f: emR.filter(d => d.tmp === "Frio").length,
    churn: churn.length, reemb,
    conv,
    net: rows.length ? (won.length - churn.length) / rows.length : 0,
    receita, receitaLiq: receita - reemb,
    ticket: won.length ? receita / won.length : 0,
    score: comNota.length ? comNota.reduce((a, d) => a + (d.an as Analise).nota, 0) / comNota.length : null,
    lista, desc: lista ? 1 - receita / lista : null,
    ...forecast(open, conv, f),
    ...receitaRet(won, receita),
    ...receitaQuente(won, receita),
    ciclo: cicloMedio(won),
  };
}

/* ---------- série do gráfico ----------
   Agrupa por semana; passando de 92 dias, por mês. A régua sai do próprio
   período escolhido, não de uma constante. */
export function serie(deals: Negocio[], f: Filtros) {
  const dias = Math.round(
    (Date.parse(f.ate + "T12:00:00") - Date.parse(f.de + "T12:00:00")) / 86400000) + 1;
  const porMes = dias > 92;
  const rotulo = (d: Date) => porMes
    ? `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
    : (() => { const x = new Date(d); x.setDate(x.getDate() - ((x.getDay() + 6) % 7));
               return x.toISOString().slice(0, 10); })();

  const buckets = new Map<string, { opp: number; won: number; churn: number }>();
  for (const d of base(deals, f)) {
    const r = dataRef(d, f); if (!r) continue;
    const k = rotulo(new Date(r + "T12:00:00"));
    if (!buckets.has(k)) buckets.set(k, { opp: 0, won: 0, churn: 0 });
    const b = buckets.get(k)!;
    b.opp++; if (d.s === "won") b.won++; if (d.churn) b.churn++;
  }
  const chaves = [...buckets.keys()].sort();
  return {
    porMes,
    pontos: chaves.map(k => {
      const b = buckets.get(k)!;
      return {
        k, opp: b.opp,
        bruta: b.opp ? b.won / b.opp : 0,
        net: b.opp ? (b.won - b.churn) / b.opp : 0,
        rot: porMes
          ? new Date(k + "-01T12:00:00").toLocaleDateString("pt-BR", { month: "short" }).replace(".", "")
          : k.slice(8, 10) + "/" + k.slice(5, 7),
      };
    }),
  };
}

/* ---------- ranking de closers, por receita ---------- */
export function ranking(rows: Negocio[], f: Filtros) {
  return [...new Set(rows.map(d => d.v))]
    .map(v => ({ v, a: agg(rows.filter(d => d.v === v), f) }))
    .sort((x, y) => y.a.receita - x.a.receita);
}

/* ---------- qualificação do que entrou, e o que virou venda ---------- */
export function qualificacao(rows: Negocio[]) {
  const letras = [...new Set(rows.map(d => d.lead).filter(Boolean))].sort() as string[];
  const semQualificacao = rows.filter(d => !d.lead).length;
  return {
    semQualificacao,
    faixas: letras.map(l => {
      const arr = rows.filter(d => d.lead === l);
      const ganhos = arr.filter(d => d.s === "won").length;
      return { lead: l, total: arr.length, ganhos,
               taxa: arr.length ? ganhos / arr.length : 0 };
    }),
  };
}

/* ---------- formatação (a camada de cima pode usar ou ignorar) ---------- */
export const BRL = (n: number) => "R$ " + Math.round(n).toLocaleString("pt-BR");
export const PCT = (n: number) =>
  (isFinite(n) ? (n * 100).toFixed(1).replace(".", ",") : "0,0") + "%";

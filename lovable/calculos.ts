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
  nota: number;
  dur: number | null;          // duração em minutos
  cp: number | null;           // % do tempo em que o closer falou
  lp: number | null;           // % do tempo em que o lead falou
  resumo: string | null;
  certo: string[]; erro: string[]; cond: string[];
  porque: string | null;
  /* Os quatro abaixo vinham da Edge Function e o painel antigo ignorava. */
  valorPitch: number | null;   // valor ofertado NA CALL
  parc: number | null;         // nº de parcelas do pitch
  nota_justificativa: string | null;  // por que a IA deu essa nota
  closer: string | null;       // nome como escrito na análise
  sdrNota: string | null;
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
  dSal: string | null;         // Data Lead Aceito pelo Closer (SAL)
  dSql: string | null;         // Data Qualificação (SQL)
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

/* ============================================================================
   CHURN
   ============================================================================
   Duas leituras do mesmo período, e elas NÃO dão o mesmo número:
   · "cancelou" — quem pediu cancelamento nestas datas, tenha vendido quando
     tiver vendido. É como o CS enxerga o mês. Usa o histórico de 12 meses.
   · "vendeu"   — das vendas destas datas, quantas caíram. É como o comercial
     enxerga a própria safra. Usa os negócios do período.
   Mostrar uma e chamar de "churn do mês" sem dizer qual é o erro clássico.   */

export const META_CHURN = 0.05;   // meta da casa, medida sobre o RECEBIMENTO
export const DIAS_PRECOCE = 7;    // cancelou em até 7 dias do ganho = precoce

/* As sete opções do campo "Motivo Churn" no Pipedrive, agrupadas por quem tem a
   mão no problema. Quatro grupos, não cinco: "Negativa contratual" está em
   Comercial — contrato que o cliente se recusa a honrar é venda mal alinhada,
   não categoria à parte. Logística/Marketplace fica sozinho: não é erro nosso
   nem problema do cliente, é a operação em volta.
   O campo é de MÚLTIPLA ESCOLHA — um cancelamento entra em mais de um motivo, e
   por isso as porcentagens somam mais de 100%. A tela precisa dizer isso. */
export const MOTIVOS_CHURN: Array<[string, string]> = [
  ["Arrependimento (comprou no impulso)",    "Comercial"],
  ["Desalinhamento no comercial",            "Comercial"],
  ["Negativa contratual",                    "Comercial"],
  ["Erro de Processo (CS)",                  "CS"],
  ["Produto do cliente",                     "Problema do Cliente"],
  ["Problemas pessoais do cliente",          "Problema do Cliente"],
  ["Logística ou problema e/ou marketplace", "Logística/Marketplace"],
];
const CULPA = new Map(MOTIVOS_CHURN);
export const areaDe = (m: string): string => CULPA.get(m) ?? "Não informado";

export const AREAS: Array<[string, string, string]> = [
  ["Comercial",             "rosa",  "venda no impulso, promessa desalinhada ou negativa contratual"],
  ["CS",                    "ambar", "falha no processo de acompanhamento"],
  ["Problema do Cliente",   "peri",  "motivo fora do nosso alcance"],
  ["Logística/Marketplace", "ciano", "logística, frete ou conta no marketplace"],
];

/** O que de fato entrou. "Valor pago" vazio cai para o valor do negócio — e a
    tela avisa quantos entraram por aproximação. */
export const recebidoDe = (d: Negocio): number => (d.valPago > 0 ? d.valPago : d.val) || 0;

export const ehPrecoce = (d: Negocio): boolean => {
  const x = difDias(d.dGanho, d.dc);
  return x != null && x <= DIAS_PRECOCE;
};

export const mesDe = (iso?: string | null) => (iso ? iso.slice(0, 7) : null);

/** Quem entra na conta de churn, conforme a aba escolhida. */
export function selecaoChurn(
  noPeriodo: Negocio[], churn12: Negocio[], f: Filtros, aba: "cancelou" | "vendeu",
) {
  const ganhos = noPeriodo.filter(d => d.s === "won");
  const doHistorico = churn12.filter(d => d.dc && d.dc >= f.de && d.dc <= f.ate);
  const doPeriodo = noPeriodo.filter(d => d.churn);
  const cs = aba === "vendeu" ? doPeriodo : (doHistorico.length ? doHistorico : doPeriodo);
  return {
    ganhos, cs, doPeriodo,
    semData: aba === "vendeu" ? 0 : doPeriodo.filter(d => !d.dc).length,
  };
}

/** Os números do topo da página. A meta é sobre o RECEBIMENTO, não sobre
    contagem de aluno — apresentar a taxa por cabeça como se fosse a meta é o
    erro que esta função existe para evitar. */
export function resumoChurn(cs: Negocio[], ganhos: Negocio[]) {
  const reemb = cs.reduce((a, d) => a + (d.reemb || 0), 0);
  const precoces = cs.filter(ehPrecoce);
  const recebido = ganhos.reduce((a, d) => a + recebidoDe(d), 0);
  const contratos = cs.reduce((a, d) => a + (d.val || 0), 0);
  return {
    cancelamentos: cs.length, reemb, contratos,
    precoces: precoces.length,
    pctPrecoce: cs.length ? precoces.length / cs.length : null,
    ticketReemb: cs.length && reemb ? reemb / cs.length : null,
    comReembolso: cs.filter(d => d.reemb > 0).length,
    recebido,
    semValorPago: ganhos.filter(d => !(d.valPago > 0)).length,
    /* a meta: reembolsado ÷ recebido */
    taxa: recebido ? reemb / recebido : null,
    /* a mesma coisa em cabeças — serve de nota de rodapé, nunca de manchete */
    taxaQtd: ganhos.length ? cs.length / ganhos.length : null,
  };
}

/** Ordenado pelo dinheiro devolvido, não pela contagem: três cancelamentos de
    R$ 500 e um de R$ 12 mil não são o mesmo problema. */
export function churnPorCloser(noPeriodo: Negocio[], cs: Negocio[]) {
  const ganhos = noPeriodo.filter(d => d.s === "won");
  const nomes = [...new Set([...noPeriodo.map(d => d.v), ...cs.map(d => d.v)])];
  return nomes.map(v => {
    const c = cs.filter(d => d.v === v);
    const g = ganhos.filter(d => d.v === v);
    return {
      v, n: c.length, ganhos: g.length,
      reemb: c.reduce((a, d) => a + (d.reemb || 0), 0),
      contrato: c.reduce((a, d) => a + (d.val || 0), 0),
      precoce: c.filter(ehPrecoce).length,
      taxa: g.length ? c.length / g.length : 0,
    };
  }).filter(x => x.ganhos || x.n)
    .sort((a, b) => b.reemb - a.reemb || b.n - a.n || b.taxa - a.taxa);
}

/** Por Buddy, com o motivo junto: sem ele o bloco diz quanto foi devolvido mas
    não POR QUE — e é o porquê que decide com quem é a conversa. */
export function churnPorBuddy(cs: Negocio[]) {
  const comBuddy = cs.filter(d => d.buddy);
  const linhas = [...new Set(comBuddy.map(d => d.buddy as string))].map(b => {
    const r = comBuddy.filter(d => d.buddy === b);
    const mot: Record<string, number> = {};
    r.forEach(d => ((d.cm as string[])?.length ? (d.cm as string[]) : ["Não informado"])
      .forEach(x => { mot[x] = (mot[x] || 0) + 1; }));
    return {
      b, n: r.length, mot,
      reemb: r.reduce((a, d) => a + (d.reemb || 0), 0),
      val: r.reduce((a, d) => a + d.val, 0),
      precoce: r.filter(ehPrecoce).length,
    };
  }).sort((a, b) => b.reemb - a.reemb || b.n - a.n);
  return { linhas, semBuddy: cs.length - comBuddy.length };
}

export function churnPorProduto(noPeriodo: Negocio[], cs: Negocio[]) {
  const ganhos = noPeriodo.filter(d => d.s === "won");
  return [...new Set([...ganhos.map(d => d.p), ...cs.map(d => d.p)])]
    .map(p => {
      const v = ganhos.filter(d => d.p === p);
      const c = cs.filter(d => d.p === p);
      return {
        p, v: v.length, c: c.length,
        taxa: v.length ? c.length / v.length : null,
        precoce: c.filter(ehPrecoce).length,
        reemb: c.reduce((a, d) => a + (d.reemb || 0), 0),
      };
    })
    .filter(x => x.v || x.c)
    .sort((a, b) => (b.taxa ?? -1) - (a.taxa ?? -1) || b.v - a.v);
}

/** De quem foi o churn. Conta CITAÇÕES de motivo, não pessoas — o campo aceita
    mais de um motivo, então a soma passa de 100% e a tela tem que falar isso. */
export function culpaDoChurn(cs: Negocio[]) {
  const cont: Record<string, { n: number; reemb: number; motivos: Record<string, number> }> = {};
  cs.forEach(d => ((d.cm as string[]) || []).forEach(m => {
    const a = areaDe(m);
    cont[a] = cont[a] || { n: 0, reemb: 0, motivos: {} };
    cont[a].n++; cont[a].reemb += d.reemb || 0;
    cont[a].motivos[m] = (cont[a].motivos[m] || 0) + 1;
  }));
  const linhas = AREAS
    .map(([nome, cor, oq]) => ({ nome, cor, oq, ...(cont[nome] || { n: 0, reemb: 0, motivos: {} }) }))
    .filter(x => x.n).sort((a, b) => b.n - a.n);
  return {
    linhas,
    citacoes: linhas.reduce((a, x) => a + x.n, 0),
    semMotivo: cs.filter(d => !(d.cm as string[])?.length).length,
  };
}

export function tempoAteCancelar(cs: Negocio[]) {
  const faixas: Array<[string, number, number]> = [
    [`Até ${DIAS_PRECOCE} dias · precoce`, 0, DIAS_PRECOCE],
    [`${DIAS_PRECOCE + 1} a 30 dias`, DIAS_PRECOCE + 1, 30],
    ["31 a 90 dias", 31, 90],
    ["Mais de 90", 91, 1e9],
  ];
  const dur = cs.map(d => difDias(d.dGanho, d.dc)).filter((x): x is number => x != null);
  return {
    comData: dur.length,
    faixas: faixas.map(([rot, a, b]) => ({ rot, n: dur.filter(x => x >= a && x <= b).length })),
  };
}

/* Cancelamentos mês a mês do ANO CIVIL do filtro — janeiro até o mês do "Até".
   Não é janela móvel: misturar dois anos no mesmo gráfico impede comparar com a
   meta do ano. A média do ano divide pelos meses DECORRIDOS, não por doze: em
   agosto, dividir por doze joga a média um terço para baixo. */
export function churnPorMes(churn12: Negocio[], f: Filtros) {
  const ano = (f.ate || "").slice(0, 4);
  const ultimo = Number((f.ate || "").slice(5, 7));
  const meses: string[] = [];
  for (let m = 1; m <= ultimo; m++) meses.push(`${ano}-${String(m).padStart(2, "0")}`);

  const dados = meses.map(mm => {
    const c = churn12.filter(d => mesDe(d.dc) === mm);
    const p = c.filter(ehPrecoce).length;
    return {
      mes: mm,
      rot: mm.slice(5) + "/" + mm.slice(2, 4),
      n: c.length, precoce: p, resto: c.length - p,
      reemb: c.reduce((a, d) => a + (d.reemb || 0), 0),
    };
  });
  const tot = dados.reduce((a, d) => a + d.n, 0);
  const totPrecoce = dados.reduce((a, d) => a + d.precoce, 0);
  const totReemb = dados.reduce((a, d) => a + d.reemb, 0);
  const nMeses = dados.length;
  return {
    ano, dados, tot, totPrecoce, totReemb, nMeses,
    mediaMes: nMeses ? totReemb / nMeses : 0,      // R$ devolvido por mês
    mediaQtd: nMeses ? tot / nMeses : 0,           // cancelamentos por mês
    pior: [...dados].sort((a, b) => b.n - a.n)[0] ?? null,
  };
}

/* ============================================================================
   CLOSERS
   ============================================================================ */

/** Faixa da nota da call, no critério ICOMM/TF. */
export const faixa = (n: number | null): string | null =>
  n == null ? null : n >= 8 ? "forte" : n >= 6.5 ? "boa" : n >= 5 ? "mediana" : "grave";

/** Negócio que entra no forecast: aberto com retorno marcado ou parado em etapa de RET. */
export const noFcst = (d: Negocio, f: Filtros): boolean =>
  d.s === "open" && !!(d.retAgendado || ETAPAS_RET(f).includes(d.et));

/** Venda que passou por retorno em algum momento. */
export const veioDeRet = (d: Negocio): boolean =>
  !!(d.retAgendado || d.retRealizado || (d.nret ?? 0) > 0);

export function perfilCloser(rows: Negocio[], v: string) {
  const r = rows.filter(d => d.v === v);
  const won = r.filter(d => d.s === "won");
  const lost = r.filter(d => d.s === "lost");
  const churn = r.filter(d => d.churn);
  const receita = won.reduce((a, d) => a + d.val, 0);
  const ciclos = won.map(d => difDias(d.dCriacao, d.dGanho))
                    .filter((x): x is number => x != null && x >= 0);
  const comLista = won.filter(d => d.precoLista > 0);
  const lista = comLista.reduce((a, d) => a + d.precoLista, 0);
  const praticado = comLista.reduce((a, d) => a + d.val, 0);
  const notas = r.filter(d => d.an).map(d => (d.an as Analise).nota);
  return {
    v, r, won, lost, churn, receita,
    opp: r.length,
    conv: r.length ? won.length / r.length : 0,
    net: r.length ? (won.length - churn.length) / r.length : 0,
    ticket: won.length ? receita / won.length : 0,
    ciclo: ciclos.length ? ciclos.reduce((a, b) => a + b, 0) / ciclos.length : null,
    desconto: lista ? 1 - praticado / lista : null,
    score: notas.length ? notas.reduce((a, b) => a + b, 0) / notas.length : null,
    nNotas: notas.length,
  };
}

/** Os números do time, no topo da página. */
export function resumoTime(noPeriodo: Negocio[], f: Filtros) {
  const perfis = [...new Set(noPeriodo.map(d => d.v))].map(v => perfilCloser(noPeriodo, v));
  const won = noPeriodo.filter(d => d.s === "won");
  const churn = noPeriodo.filter(d => d.churn);
  const receita = won.reduce((a, d) => a + d.val, 0);
  const ciclos = perfis.map(p => p.ciclo).filter((x): x is number => x != null);
  return {
    perfis,
    opp: noPeriodo.length, won: won.length, churn: churn.length, receita,
    conv: noPeriodo.length ? won.length / noPeriodo.length : 0,
    net: noPeriodo.length ? (won.length - churn.length) / noPeriodo.length : 0,
    ticket: won.length ? receita / won.length : 0,
    ciclo: ciclos.length ? ciclos.reduce((a, b) => a + b, 0) / ciclos.length : null,
  };
}

/* Vendedor › Produto › Lead, ordenado por RECEITA em cada nível — quem vendeu
   mais fica em cima. Empate em zero desempata por volume de oportunidades e
   depois por nome, para a ordem não dançar entre uma carga e outra. */
function porReceita<T>(lista: Negocio[], chave: (d: Negocio) => string, f: Filtros) {
  return [...new Set(lista.map(chave))]
    .map(k => {
      const r = lista.filter(d => chave(d) === k);
      const a = agg(r, f);
      return { k, r, a, receita: a.receita, opp: a.opp };
    })
    .sort((x, y) => y.receita - x.receita || y.opp - x.opp
                 || String(x.k).localeCompare(String(y.k), "pt-BR"));
}

export function hierarquia(noPeriodo: Negocio[], f: Filtros) {
  return porReceita(noPeriodo, d => d.v, f).map(v => ({
    ...v,
    produtos: porReceita(v.r, d => d.p, f).map(p => ({
      ...p,
      negocios: [...p.r].sort((a, b) => b.val - a.val),
    })),
  }));
}

/** Nos níveis agregados, o topo da distribuição de qualificação (ex.: B 5 · A 3). */
export function mixLead(rows: Negocio[]) {
  const c: Record<string, number> = {};
  rows.forEach(d => { if (d.lead) c[d.lead] = (c[d.lead] || 0) + 1; });
  return Object.entries(c).sort((x, y) => y[1] - x[1]).slice(0, 2)
    .map(([lead, n]) => ({ lead, n }));
}

/** Busca e filtro de nota da tabela de negócios. Valem só ali — os filtros do
    topo continuam mandando no resto da página. */
export function filtraDeals(
  rows: Negocio[], busca: string, an: "" | "com" | "sem" | "8" | "65" | "5",
) {
  const q = busca.trim().toLowerCase();
  const campos = (d: Negocio) =>
    [d.t, d.v, d.p, d.et, d.canal, d.lead, d.sdr, d.orig, String(d.id)]
      .filter(Boolean).join(" ").toLowerCase();
  return rows.filter(d => {
    if (q && !campos(d).includes(q)) return false;
    const n = d.an?.nota;
    if (an === "com" && !d.an) return false;
    if (an === "sem" && d.an) return false;
    if (an === "8" && !(n != null && n >= 8)) return false;
    if (an === "65" && !(n != null && n >= 6.5 && n < 8)) return false;
    if (an === "5" && !(n != null && n < 6.5)) return false;
    return true;
  });
}

/** Motivos de perda mais frequentes por closer — para achar padrão, não culpado. */
export function motivosDePerda(noPeriodo: Negocio[], quantos = 3) {
  return [...new Set(noPeriodo.map(d => d.v))]
    .map(v => {
      const lost = noPeriodo.filter(d => d.v === v && d.s === "lost");
      const m: Record<string, number> = {};
      lost.forEach(d => { const k = (d.lm as string) || "Sem motivo"; m[k] = (m[k] || 0) + 1; });
      return {
        v, perdas: lost.length,
        top: Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, quantos)
          .map(([motivo, n]) => ({ motivo, n })),
      };
    })
    .filter(x => x.perdas)
    .sort((a, b) => b.perdas - a.perdas);
}

/* ============================================================================
   REUNIÕES
   ============================================================================ */

/* O desconto que interessa é sobre o que o closer OFERTOU NA CALL, não sobre o
   preço de catálogo: metade dos produtos não está cadastrada em Produtos no
   Pipedrive, e aí precoLista vem zero e o desconto vira "—". O valor do pitch
   a IA capturou da própria call. */
export const descontoDoPitch = (d: Negocio): number | null => {
  const pitch = d.an?.valorPitch;
  if (!pitch || pitch <= 0 || d.s !== "won" || !d.val) return null;
  return 1 - d.val / pitch;
};

/** Frases que se repetem entre calls diferentes, agrupadas pelo começo. Serve
    tanto para erro quanto para acerto: o padrão é o que interessa, não a frase
    isolada de uma call. */
export function frasesRecorrentes(
  linhas: string[][], minimo = 2, quantos = 6,
): Array<{ frase: string; n: number; exemplo: string }> {
  const m: Record<string, { n: number; ex: string }> = {};
  linhas.forEach(arr => (arr || []).forEach(e => {
    const k = e.split(/[:.]/)[0].trim().slice(0, 60);
    if (k.length < 6) return;
    m[k] = m[k] || { n: 0, ex: e };
    m[k].n++;
  }));
  return Object.entries(m)
    .filter(([, v]) => v.n >= minimo)
    .sort((a, b) => b[1].n - a[1].n)
    .slice(0, quantos)
    .map(([frase, v]) => ({ frase, n: v.n, exemplo: v.ex }));
}

/** Score da call por produto — pedido do head. Diz qual produto o time sabe
    vender e qual ele apanha para explicar. */
export function scorePorProduto(rows: Negocio[]) {
  const comAn = rows.filter(d => d.an);
  return [...new Set(comAn.map(d => d.p))].map(p => {
    const r = comAn.filter(d => d.p === p);
    const notas = r.map(d => (d.an as Analise).nota);
    const won = r.filter(d => d.s === "won");
    const lost = r.filter(d => d.s === "lost");
    const fech = won.length + lost.length;
    const cf = r.filter(d => (d.an as Analise).cp != null);
    const descs = r.map(descontoDoPitch).filter((x): x is number => x != null);
    return {
      p, n: r.length,
      media: notas.reduce((a, b) => a + b, 0) / notas.length,
      pior: Math.min(...notas), melhor: Math.max(...notas),
      won: won.length, lost: lost.length,
      conv: fech ? won.length / fech : null,
      receita: won.reduce((a, d) => a + d.val, 0),
      fala: cf.length ? cf.reduce((a, d) => a + ((d.an as Analise).cp as number), 0) / cf.length : null,
      desconto: descs.length ? descs.reduce((a, b) => a + b, 0) / descs.length : null,
    };
  }).sort((a, b) => a.media - b.media);   // o pior primeiro: é onde se age
}

/* Resumo por closer — pedido da proprietária, para não ler call a call.
   NÃO é texto gerado: é o que as próprias análises já disseram, agrupado. Cada
   linha aqui é rastreável até a call que a originou, e isso é melhor do que
   prosa nova, que ninguém consegue conferir. */
export function resumoPorCloser(rows: Negocio[]) {
  const comAn = rows.filter(d => d.an);
  return [...new Set(comAn.map(d => d.v))].map(v => {
    const r = comAn.filter(d => d.v === v);
    const todas = rows.filter(d => d.v === v);
    const an = r.map(d => d.an as Analise);
    const notas = an.map(a => a.nota);
    const cf = an.filter(a => a.cp != null);
    const dur = an.filter(a => a.dur);
    const won = r.filter(d => d.s === "won");
    const lost = r.filter(d => d.s === "lost");
    const fech = won.length + lost.length;
    const descs = r.map(descontoDoPitch).filter((x): x is number => x != null);

    /* objeções que ele mais enfrenta, e quanto contorna. Só as ouvidas NA
       REUNIÃO: a que vem do motivo da perda está, por definição, em negócio
       perdido, e daria 0% de contorno para todo mundo. */
    const objm: Record<string, { n: number; won: number }> = {};
    r.forEach(d => ((d.obj as Array<{ nome: string; origem: string }>) || [])
      .filter(o => o.origem === "call")
      .forEach(o => {
        objm[o.nome] = objm[o.nome] || { n: 0, won: 0 };
        objm[o.nome].n++;
        if (d.s === "won") objm[o.nome].won++;
      }));

    return {
      v, calls: r.length, negocios: todas.length,
      media: notas.reduce((a, b) => a + b, 0) / notas.length,
      pior: Math.min(...notas), melhor: Math.max(...notas),
      fala: cf.length ? cf.reduce((a, x) => a + (x.cp as number), 0) / cf.length : null,
      monologos: cf.filter(a => (a.cp as number) >= 75).length,
      duracao: dur.length ? dur.reduce((a, x) => a + (x.dur as number), 0) / dur.length : null,
      won: won.length, lost: lost.length,
      conv: fech ? won.length / fech : null,
      receita: won.reduce((a, d) => a + d.val, 0),
      desconto: descs.length ? descs.reduce((a, b) => a + b, 0) / descs.length : null,
      parcelaMedia: (() => {
        const ps = an.map(a => a.parc).filter((x): x is number => !!x);
        return ps.length ? ps.reduce((a, b) => a + b, 0) / ps.length : null;
      })(),
      /* mínimo 2: uma frase que apareceu numa call só é anedota, não padrão */
      erros: frasesRecorrentes(an.map(a => a.erro), 2, 3),
      acertos: frasesRecorrentes(an.map(a => a.certo), 2, 3),
      objecoes: Object.entries(objm)
        .sort((a, b) => b[1].n - a[1].n).slice(0, 3)
        .map(([nome, x]) => ({ nome, n: x.n, contorno: x.n ? x.won / x.n : 0 })),
    };
  }).sort((a, b) => b.media - a.media);
}

/* ============================================================================
   SAL — Sales Accepted Lead
   ============================================================================
   O dia em que o CLOSER aceitou o lead. Existe porque "ciclo de venda" medido
   da criação do negócio até o ganho mistura o tempo do SDR com o do closer, e
   cobra do closer um atraso que pode não ser dele. Da aceitação até o ganho é
   só o tempo dele.

   Vem preenchido em negócio ganho. Em negócio aberto costuma vir vazio: a API
   v2 traz no máximo 15 campos customizados e este não está entre eles — por
   isso as funções abaixo sempre dizem sobre quantos negócios calcularam.      */

/** Da aceitação do lead até o ganho — o ciclo que é do closer. */
export const cicloDoCloser = (d: Negocio): number | null =>
  d.s === "won" ? difDias(d.dSal as string | null, d.dGanho) : null;

/** Da qualificação até o closer aceitar — quanto o lead esperou na mão dele. */
export const tempoDeAceite = (d: Negocio): number | null =>
  difDias(d.dSql as string | null, d.dSal as string | null);

export function salPorCloser(rows: Negocio[]) {
  return [...new Set(rows.map(d => d.v))].map(v => {
    const r = rows.filter(d => d.v === v);
    const aceitos = r.filter(d => d.dSal);
    const ciclos = r.map(cicloDoCloser).filter((x): x is number => x != null && x >= 0);
    const aceites = r.map(tempoDeAceite).filter((x): x is number => x != null && x >= 0);
    const won = r.filter(d => d.s === "won");
    const media = (a: number[]) => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
    return {
      v,
      negocios: r.length,
      /* sem isto o número engana: média de 3 negócios não é a média do closer */
      comSal: aceitos.length,
      cobertura: r.length ? aceitos.length / r.length : 0,
      aceitos: aceitos.length,
      ganhos: won.length,
      convAceitos: aceitos.length ? won.filter(d => d.dSal).length / aceitos.length : null,
      cicloCloser: media(ciclos), nCiclo: ciclos.length,
      aceite: media(aceites), nAceite: aceites.length,
    };
  }).filter(x => x.negocios)
    .sort((a, b) => (a.cicloCloser ?? 1e9) - (b.cicloCloser ?? 1e9));
}

/* ============================================================================
   RETORNO
   ============================================================================
   Três abas, três perguntas diferentes — e é por isso que elas usam réguas de
   data diferentes:

   · Carteira  — em que pé está cada retorno AGORA. Bloco de ESTADO: lê a
                 carteira aberta inteira, vista a partir da data de referência
                 (o "Até"). Não leva recorte de intervalo. "Vencido" é estado
                 acumulado, não evento: retorno marcado para 19/08 e não feito
                 continua vencido no dia 24. Filtrar [24/08 a 24/08] exigiria
                 que o retorno tivesse sido marcado exatamente naquele dia — e
                 zerava a tela inteira com 29 negócios abertos.
   · Lastro    — o que as reuniões DO PERÍODO renderam. Bloco de EVENTO: leva o
                 intervalo do topo.
   · Funil     — a conversão das reuniões do período. Bloco de EVENTO também.

   O gráfico "Retornos por dia" mora na Carteira mas é EVENTO: a barra é o dia
   agendado, dentro do intervalo. Por isso filtrar um dia mostra a barra
   daquele dia, com os cartões acima ainda contando a carteira inteira. */

/** A data de onde se olha o funil. Não é janela: é o dia em que a foto foi tirada. */
export const refISO = (f: Filtros): string => f.ate;

/* Etapas que contam como retorno mesmo sem nenhuma data preenchida. Ignoram de
   propósito o filtro "ret" do topo: Follow UP é o caso mais grave (ninguém
   marcou nada) e não pode sumir da tela por causa de um seletor. */
export const ETAPAS_RET_FIXAS = ["Retorno Agendado", "Retorno Realizado", "Follow UP"];

export const carteiraRet = (deals: Negocio[], f: Filtros): Negocio[] =>
  carteira(deals, f).filter(d =>
    ETAPAS_RET_FIXAS.includes(d.et) || d.et === "No Show" ||
    d.retAgendado || d.retRealizado || d.noShow);

/* Só 7% preenchem "Data Retorno Realizado" e 2% "Data NoShow" — mas a etapa do
   funil é movida. Então a etapa vale como registro quando a data falta. */
export const foiRealizado = (d: Negocio): boolean =>
  !!d.retRealizado || d.et === "Retorno Realizado";
export const foiNoShow = (d: Negocio): boolean =>
  !!d.noShow || d.et === "No Show";

export type EstadoRet =
  | "vencido" | "hoje" | "futuro" | "noshow" | "reagendado" | "realizado" | "semdata";

/* Em que pé está o retorno deste negócio.
   A ordem importa: reagendado ganha de no-show, e no-show ganha de vencido —
   senão o closer que correu atrás aparece como se não tivesse feito nada. */
export function estadoRet(d: Negocio, f: Filtros): EstadoRet | null {
  if (d.s !== "open") return null;
  const ag = d.retAgendado;
  const hoje = refISO(f);
  const rz = d.retRealizado || (d.et === "Retorno Realizado" ? (d.retAgendado || hoje) : null);
  const ns = d.noShow      || (d.et === "No Show"           ? (d.retAgendado || hoje) : null);
  if (ns && ag && ag > ns)     return "reagendado";
  if (ns && (!ag || ag <= ns)) return "noshow";
  if (rz && (!ag || rz >= ag)) return "realizado";
  if (!ag)                     return "semdata";
  if (ag > hoje)               return "futuro";
  if (ag === hoje)             return "hoje";
  return "vencido";
}

export const ROTULO_EST: Record<EstadoRet, string> = {
  vencido: "Vencido", hoje: "Hoje", futuro: "Agendado", noshow: "Lead não apareceu",
  reagendado: "Reagendado", realizado: "Realizado", semdata: "Sem data",
};

/* Vencido primeiro: a tela é fila de trabalho, não relatório. */
export const PESO_EST: Record<EstadoRet, number> = {
  vencido: 0, semdata: 1, noshow: 2, hoje: 3, reagendado: 4, futuro: 5, realizado: 6,
};
/* A ordem dos chips da lista, e ela NÃO é a mesma do PESO_EST acima.
   "realizado" fica de fora de propósito: o negócio continua na lista e entra no
   chip "Todos", mas não ganha botão próprio — a lista é fila de trabalho, e
   retorno já realizado não é trabalho pendente. Efeito colateral: a soma dos
   chips não fecha com o "Todos" quando existe algum realizado na carteira. */
export const ORDEM_EST: EstadoRet[] =
  ["vencido", "semdata", "noshow", "hoje", "futuro", "reagendado"];

/* ---------- os quatro cartões de ação ---------- */
/* Não existe cartão "Amanhã": ele olhava para fora do período. Amanhã aparece
   quando o "Até" alcança amanhã — a tela obedece o filtro, não o contrário. */
export function cartoesRet(rows: Negocio[], f: Filtros) {
  const por = (e: EstadoRet) => rows.filter(d => estadoRet(d, f) === e);
  const soma = (a: Negocio[]) => a.reduce((x, d) => x + d.val, 0);
  const cartao = (chave: EstadoRet, rotulo: string, vazio: string) => {
    const deals = por(chave);
    return { chave, rotulo, deals, n: deals.length, valor: soma(deals), vazio };
  };
  return [
    cartao("vencido", "Vencidos", "passou da data e ninguém registrou"),
    cartao("hoje", "Hoje", "acontece na data de referência"),
    cartao("noshow", "Lead não apareceu", "no-show sem reagendar"),
    cartao("semdata", "Sem data", "ninguém marcou nada"),
  ];
}

/* ---------- lastro: a reunião saiu com retorno marcado? ---------- */
/* A pergunta do gestor de manhã. Lê D inteiro, não a carteira: reunião que já
   virou venda ou perda também teve lastro, e sumiria se lêssemos só os abertos. */
export function lastro(deals: Negocio[], f: Filtros) {
  const reunioes = deals.filter(d => filtrosComuns(d, f))
    .filter(d => d.diaReuniao && d.diaReuniao >= f.de && d.diaReuniao <= f.ate);
  const temRetorno = (d: Negocio) => !!(d.retAgendado || d.retRealizado);
  const comRet = reunioes.filter(temRetorno);
  const noShow = reunioes.filter(d => !temRetorno(d) && !!d.noShow);
  const sem    = reunioes.filter(d => !temRetorno(d) && !d.noShow);

  const porCloser = [...new Set(reunioes.map(d => d.v))]
    .map(v => {
      const r = reunioes.filter(d => d.v === v);
      const ok = r.filter(temRetorno).length;
      const ns = r.filter(d => !temRetorno(d) && !!d.noShow).length;
      return {
        v, deals: r, total: r.length, ok, ns, nada: r.length - ok - ns,
        linhas: r.map(d => ({
          d,
          estado: temRetorno(d) ? "ok" : d.noShow ? "ns" : "nada" as "ok" | "ns" | "nada",
        })),
      };
    })
    .sort((a, b) => b.total - a.total);

  return { reunioes, comRet, noShow, sem, porCloser };
}

/* ---------- retornos por dia ---------- */
/* Junta o que eram dois blocos — "agenda dos próximos dias" e "forecast por
   dia". Era o mesmo dado desenhado duas vezes, um olhando para a frente e outro
   para o período, e eles se contradiziam na tela.

   A janela é o período do topo e nada além dele. Antes esticava 14 dias à
   frente por conta própria, e aí o gráfico discordava dos cartões logo acima.
   Quem quiser ver o que vem estica o "Até" — e `depois` diz quantos ficaram de
   fora, para a pessoa decidir se vale. */
export const TEMPS_RET: Array<string | null> = ["Quente", "Morno", "Frio", null];

export function retornosPorDia(cr: Negocio[], f: Filtros) {
  const ag = cr.filter(d => d.retAgendado && d.retAgendado >= f.de && d.retAgendado <= f.ate);
  const depois = cr.filter(d => d.retAgendado && d.retAgendado > f.ate).length;
  if (!ag.length) return { vazio: true as const, ag, depois, dias: [], porDia: [], porCloser: [],
                           passado: [], futuro: [], total: 0 };

  const dias = [...new Set(ag.map(d => d.retAgendado as string))].sort();
  const porDia = dias.map(dt => {
    const arr = ag.filter(d => d.retAgendado === dt);
    return {
      dt, n: arr.length, total: arr.reduce((a, d) => a + d.val, 0),
      hoje: dt === refISO(f),
      partes: TEMPS_RET.map(t => ({
        t, valor: arr.filter(d => (d.tmp || null) === t).reduce((a, d) => a + d.val, 0),
      })),
    };
  });

  const passado = ag.filter(d => (d.retAgendado as string) < refISO(f));
  const futuro  = ag.filter(d => (d.retAgendado as string) >= refISO(f));

  const porCloser = [...new Set(ag.map(d => d.v || "Sem vendedor"))].map(v => {
    const arr = ag.filter(d => (d.v || "Sem vendedor") === v).slice()
      .sort((a, b) => (a.retAgendado || "").localeCompare(b.retAgendado || "") || b.val - a.val);
    const cel = (t: string) => {
      const a = arr.filter(d => (d.tmp || null) === t);
      return { n: a.length, v: a.reduce((x, d) => x + d.val, 0) };
    };
    return {
      v, deals: arr, n: arr.length, val: arr.reduce((a, d) => a + d.val, 0),
      atras: arr.filter(d => (d.retAgendado as string) < refISO(f)).length,
      q: cel("Quente"), m: cel("Morno"), f: cel("Frio"),
    };
  }).sort((a, b) => b.val - a.val || b.n - a.n);

  return {
    vazio: false as const, ag, depois, dias, porDia, porCloser, passado, futuro,
    total: ag.reduce((a, d) => a + d.val, 0),
    legenda: TEMPS_RET.map(t => ({ t, n: ag.filter(d => (d.tmp || null) === t).length })),
  };
}

/* ---------- a lista única, com busca e chips ---------- */
/* Antes eram três tabelas com o mesmo conteúdo e filtros diferentes: fila de
   trabalho, carteira inteira e lista do forecast. Agora é uma só, e os estados
   viraram botões.

   A busca corta ANTES dos chips, então o número do chip bate com o que a tabela
   mostra. Buscar e clicar num estado se somam, não competem. */
export function listaRet(
  todos: Negocio[], f: Filtros, busca = "", estado: EstadoRet | "" = "",
) {
  const q = busca.trim().toLowerCase();
  const campos = (d: Negocio) =>
    [d.t, d.v, d.p, d.et, d.canal, d.lead, d.tmp, String(d.id)]
      .filter(Boolean).join(" ").toLowerCase();
  const cr = q ? todos.filter(d => campos(d).includes(q)) : todos;

  const porEstado = {} as Record<EstadoRet, Negocio[]>;
  cr.forEach(d => {
    const e = estadoRet(d, f);
    if (e) (porEstado[e] = porEstado[e] || []).push(d);
  });

  const chips = [{
    chave: "" as const, rotulo: "Todos", n: cr.length,
    valor: cr.reduce((a, d) => a + d.val, 0),
  }].concat(
    ORDEM_EST.filter(e => porEstado[e]?.length).map(e => ({
      chave: e as never, rotulo: ROTULO_EST[e], n: porEstado[e].length,
      valor: porEstado[e].reduce((a, d) => a + d.val, 0),
    })),
  );

  const lista = (estado ? (porEstado[estado] || []) : cr).slice()
    .sort((a, b) =>
      PESO_EST[estadoRet(a, f) as EstadoRet] - PESO_EST[estadoRet(b, f) as EstadoRet] ||
      (a.retAgendado || "9999").localeCompare(b.retAgendado || "9999") ||
      b.val - a.val);

  return {
    lista, chips, porEstado, total: todos.length,
    valor: lista.reduce((a, d) => a + d.val, 0),
    /** dias de atraso — só faz sentido para quem está vencido */
    atrasoDe: (d: Negocio) =>
      estadoRet(d, f) === "vencido" ? difDias(d.retAgendado, refISO(f)) : null,
  };
}

/* ---------- funil do retorno ---------- */
/* Aninhado: cada etapa é um subconjunto da anterior. Sem isso as porcentagens
   passam de 100% e o funil vira enfeite.

   A fonte é D inteiro filtrado, NÃO base(): base() já vem recortado por data de
   desfecho, então o funil exigia que o negócio tivesse sido fechado E a reunião
   acontecido na mesma janela. Quase nada satisfaz as duas — era por isso que
   dava zero reuniões com o Lastro logo ao lado mostrando seis. */
export function funilRet(rows: Negocio[], f: Filtros) {
  const reunioes   = rows.filter(d => d.diaReuniao && d.diaReuniao >= f.de && d.diaReuniao <= f.ate);
  const agendados  = reunioes.filter(d => d.retAgendado || foiRealizado(d) || foiNoShow(d));
  const realizados = agendados.filter(foiRealizado);
  const ganhos     = realizados.filter(d => d.s === "won");
  return { reunioes, agendados, realizados, ganhos };
}

export function cartoesFunil(rows: Negocio[], f: Filtros) {
  const g = funilRet(rows, f);
  const taxa = (a: number, b: number) => (b ? a / b : null);
  return {
    ...g,
    taxaAgendou:  taxa(g.agendados.length, g.reunioes.length),
    taxaRealizou: taxa(g.realizados.length, g.agendados.length),
    taxaVenda:    taxa(g.ganhos.length, g.realizados.length),
    /** quantos retornos custa fechar uma venda */
    porVenda: g.ganhos.length ? g.realizados.length / g.ganhos.length : null,
  };
}

export const CORTES_RET = {
  v:          { titulo: "Closer",         chave: (d: Negocio) => d.v || "Sem vendedor" },
  canal:      { titulo: "Canal",          chave: (d: Negocio) => d.canal || "Sem canal" },
  plataforma: { titulo: "Onde aconteceu", chave: (d: Negocio) => (d.plataforma as string) || "Não identificada" },
};

export function corteRet(rows: Negocio[], f: Filtros, qual: keyof typeof CORTES_RET) {
  const { chave } = CORTES_RET[qual];
  const linhas = [...new Set(rows.map(chave))]
    .map(k => {
      const r = rows.filter(d => chave(d) === k);
      const g = funilRet(r, f);
      return { k, deals: r, ...g, receita: g.ganhos.reduce((a, d) => a + d.val, 0) };
    })
    .filter(x => x.reunioes.length || x.agendados.length || x.ganhos.length)
    .sort((a, b) => b.agendados.length - a.agendados.length || b.receita - a.receita);
  return { linhas, total: funilRet(rows, f), titulo: CORTES_RET[qual].titulo };
}

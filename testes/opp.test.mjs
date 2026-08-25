/* OPP é UM campo só: Dia Oportunidade. Closers tem que dar o mesmo que SDR.
   node --experimental-strip-types testes/opp.test.mjs                       */
import * as N from "../lovable/calculos.ts";
import assert from "node:assert";

let n = 0, falhou = false;
const ok = (nome, fn) => {
  try { fn(); console.log("✅ " + nome); n++; }
  catch (e) { console.log("❌ " + nome + "\n   " + e.message); falhou = true; }
};

let q = 0;
const mk = (o) => Object.assign({
  id: ++q, t: "N" + q, v: "Christopher", p: "Comercial", et: "Proposta Enviada",
  s: "open", val: 0, canal: null, lead: null, sdr: null, orig: null, tmp: null,
  dCriacao: "2026-08-02", dGanho: null, dPerda: null, dDesfecho: "2026-08-02",
  diaOpp: null, retAgendado: null, retRealizado: null, nret: 0, an: null,
  churn: false, reemb: 0, precoLista: 0,
}, o);

const f = { de: "2026-08-01", ate: "2026-08-31", basedata: "desfecho" };

const deals = [
  // oportunidade em agosto E ganho em agosto
  mk({ diaOpp: "2026-08-03", s: "won", val: 15000, dGanho: "2026-08-10", dDesfecho: "2026-08-10" }),
  // oportunidade em agosto, ainda aberto — conta como OPP, não some
  mk({ diaOpp: "2026-08-05" }),
  // oportunidade em agosto, perdido em agosto
  mk({ diaOpp: "2026-08-06", s: "lost", dPerda: "2026-08-20", dDesfecho: "2026-08-20" }),
  // ganho em agosto de uma oportunidade de JULHO: entra na receita, não na OPP
  mk({ diaOpp: "2026-07-15", s: "won", val: 9000, dGanho: "2026-08-12", dDesfecho: "2026-08-12" }),
  // aberto criado em agosto SEM Dia Oportunidade: era ele que inflava a conta
  mk({ diaOpp: null }),
  // oportunidade de agosto de outro closer, sem nenhum desfecho
  mk({ diaOpp: "2026-08-07", v: "Ellen Costa" }),
];

const noPeriodo = N.base(deals, f);
const opps = N.oppsNoPeriodo(deals, f);

ok("OPP conta o Dia Oportunidade, e nao a data de desfecho", () => {
  assert.equal(opps.length, 4);
  assert.equal(noPeriodo.length, 6);   // o que base() pegava antes
});

ok("aberto sem Dia Oportunidade nao vira oportunidade", () =>
  assert.ok(!opps.some(d => d.diaOpp == null)));

ok("a conversao usa a OPP como denominador", () => {
  const a = N.agg(noPeriodo, f, undefined, opps);
  assert.equal(a.opp, 4);
  assert.equal(a.won, 2);            // os dois ganhos de agosto
  assert.equal(a.conv, 0.5);         // 2 de 4, e nao 2 de 6
});

ok("a receita continua sendo a de quem GANHOU no periodo", () =>
  assert.equal(N.agg(noPeriodo, f, undefined, opps).receita, 24000));

ok("sem passar opps, nada muda para as outras paginas", () => {
  const a = N.agg(noPeriodo, f);
  assert.equal(a.opp, 6);
});

ok("closer com oportunidade e sem desfecho aparece na tabela", () => {
  const h = N.hierarquia(noPeriodo, f, opps);
  const ellen = h.find(v => v.k === "Ellen Costa");
  assert.ok(ellen, "Ellen sumiu da tabela");
  assert.equal(ellen.a.opp, 1);
  assert.equal(ellen.a.won, 0);
});

ok("a soma da coluna OPP da tabela bate com o total", () =>
  assert.equal(N.hierarquia(noPeriodo, f, opps).reduce((a, v) => a + v.a.opp, 0),
               opps.length));

ok("o card do topo usa o mesmo denominador da tabela", () => {
  const t = N.resumoTime(noPeriodo, f, opps);
  assert.equal(t.opp, 4);
  assert.equal(t.conv, 0.5);
});

console.log(`\n${n} conferências` + (falhou ? " — TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

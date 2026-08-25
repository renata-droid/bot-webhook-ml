/* A meta do mês: quantas OPPs e quantos ganhos ela exige, e onde estamos.
   node --experimental-strip-types testes/meta.test.mjs                      */
import * as N from "../lovable/calculos.ts";
import assert from "node:assert";

let n = 0, falhou = false;
const ok = (nome, fn) => {
  try { fn(); console.log("✅ " + nome); n++; }
  catch (e) { console.log("❌ " + nome + "\n   " + e.message); falhou = true; }
};

let q = 0;
const mk = (o) => Object.assign({
  id: ++q, t: "N" + q, v: "Lucas", p: "Comercial", et: "Proposta Enviada",
  s: "open", val: 0, canal: null, lead: null, sdr: null, orig: null,
  dCriacao: "2026-07-01", dGanho: null, diaOpp: "2026-07-01",
  retAgendado: null, retRealizado: null, nret: 0, tmp: null, an: null,
  churn: false, reemb: 0, precoLista: 0,
}, o);

const fRef = { de: "2026-07-01", ate: "2026-07-31" };
/* referência: 10 oportunidades, 2 ganhos de R$ 12.070 -> ticket 12.070, conv 20% */
const refRows = [
  ...Array.from({ length: 8 }, () => mk({ s: "lost" })),
  mk({ s: "won", val: 12070, dGanho: "2026-07-10" }),
  mk({ s: "won", val: 12070, dGanho: "2026-07-20" }),
];
const ref = N.referencia(refRows, fRef);

ok("a regua sai do periodo fechado: ticket e conversao", () => {
  assert.equal(ref.ticket, 12070);
  assert.equal(ref.conv, 0.2);
});

/* meta 1.207.000 / ticket 12.070 = 100 ganhos; 100 / 0,2 = 500 oportunidades */
const zerado = { receita: 0, won: 0, opp: 0 };
ok("a meta vira quantidade: 100 ganhos e 500 oportunidades", () => {
  const m = N.metaDoMes(zerado, ref);
  assert.equal(m.precisa.ganhos, 100);
  assert.equal(m.precisa.opps, 500);
});

ok("no meio do mes mostra o quanto ja andamos", () => {
  const m = N.metaDoMes({ receita: 603500, won: 50, opp: 200 }, ref);
  assert.equal(m.atingido.receita, 0.5);
  assert.equal(m.atingido.ganhos, 0.5);
  assert.equal(m.atingido.opps, 0.4);
  assert.equal(m.falta.receita, 603500);
  assert.equal(m.falta.opps, 300);
});

ok("bateu a meta: falta zero, e nao falta negativo", () => {
  const m = N.metaDoMes({ receita: 1_500_000, won: 120, opp: 600 }, ref);
  assert.equal(m.falta.receita, 0);
  assert.equal(m.falta.ganhos, 0);
  assert.equal(m.falta.opps, 0);
  assert.ok(m.atingido.receita > 1);
});

ok("referencia sem ganho nenhum: tracinho, nao Infinity", () => {
  const vazia = N.referencia([mk({ s: "lost" })], fRef);
  const m = N.metaDoMes(zerado, vazia);
  assert.equal(m.precisa.ganhos, null);
  assert.equal(m.precisa.opps, null);
  assert.equal(m.falta.ganhos, null);
  assert.equal(m.atingido.opps, null);
});

console.log(`\n${n} conferências` + (falhou ? " — TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

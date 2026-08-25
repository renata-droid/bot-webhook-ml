/* A meta do mês: ela é copiada do forecast do financeiro, não recalculada.
   node --experimental-strip-types testes/meta.test.mjs                      */
import * as N from "../lovable/calculos.ts";
import assert from "node:assert";

let n = 0, falhou = false;
const ok = (nome, fn) => {
  try { fn(); console.log("✅ " + nome); n++; }
  catch (e) { console.log("❌ " + nome + "\n   " + e.message); falhou = true; }
};

const zerado = { receita: 0, won: 0, opp: 0 };

ok("agosto/26 e o que o financeiro decidiu, sem recalculo", () => {
  const m = N.metaDoMes(zerado, "2026-08");
  assert.deepEqual(m.precisa, { receita: 1207500, ganhos: 85, opps: 330 });
});

ok("a regua embutida na meta bate com o dash do financeiro", () => {
  const m = N.metaDoMes(zerado, "2026-08");
  assert.equal(Math.round(m.ticketMeta), 14206);          // TICKET MÉDIO META
  assert.equal(Math.round(m.convMeta * 1000) / 10, 25.8); // CONVERSÃO META
});

ok("no meio do mes mostra feito, falta e o quanto andamos", () => {
  const m = N.metaDoMes({ receita: 603750, won: 40, opp: 165 }, "2026-08");
  assert.equal(m.atingido.receita, 0.5);
  assert.equal(m.atingido.opps, 0.5);
  assert.equal(m.falta.ganhos, 45);
});

ok("bateu a meta: falta zero, e o percentual passa de 100", () => {
  const m = N.metaDoMes({ receita: 1_500_000, won: 100, opp: 400 }, "2026-08");
  assert.equal(m.falta.receita, 0);
  assert.equal(m.falta.ganhos, 0);
  assert.ok(m.atingido.receita > 1);
});

ok("mes sem meta definida devolve null — a tela diz isso, nao inventa", () =>
  assert.equal(N.metaDoMes(zerado, "2026-09"), null));

ok("o mes sai da data FINAL do filtro", () =>
  assert.equal(N.mesDe("2026-08-25"), "2026-08"));

console.log(`\n${n} conferências` + (falhou ? " — TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

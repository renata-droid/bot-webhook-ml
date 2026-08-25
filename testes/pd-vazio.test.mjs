/* O Pipedrive devolve 200 com o corpo vazio. E aí?
   node --experimental-strip-types testes/pd-vazio.test.mjs

   Este caso derrubou o painel numa manhã: a mensagem que chegava era
   "Unexpected end of JSON input", que não diz qual chamada falhou nem se vale
   tentar de novo. */
import { empacota, roda } from "./live-harness.mjs";
import assert from "node:assert";

const HOJE = new Date().toISOString().slice(0, 10);
const bundle = empacota("supabase/functions/sdr/index.ts", "sdr-vazio");

let n = 0, falhou = false;
const ok = (nome, fn) => {
  try { fn(); console.log("\u2705 " + nome); n++; }
  catch (e) { console.log("\u274c " + nome + "\n   " + e.message); falhou = true; }
};

/* ---- 1) vazio sempre: tem que desistir com uma mensagem que se entende ---- */
let chamadasDealFields = 0;
const sempreVazio = (u) => {
  if (u.pathname === "/api/v1/dealFields") { chamadasDealFields++; return "VAZIO"; }
  return { data: [] };
};
const A = await roda(bundle, sempreVazio, { de: HOJE, ate: HOJE });

ok("desiste e diz QUAL chamada falhou", () => {
  assert.equal(A.json.ok, false);
  assert.match(A.json.erro, /corpo VAZIO/);
  assert.match(A.json.erro, /dealFields/);
});

ok("tenta de novo antes de desistir (corpo vazio e transitorio)", () =>
  assert.ok(chamadasDealFields >= 4, "tentativas: " + chamadasDealFields));

/* ---- 2) vazio na primeira, bom na segunda: tem que se recuperar sozinho ---- */
let vez = 0;
const vazioSoUmaVez = (u) => {
  if (u.pathname === "/api/v1/dealFields" && vez++ === 0) return "VAZIO";
  if (u.pathname === "/api/v1/dealFields") return { data: [] };
  if (u.pathname === "/api/v1/users") return { data: [] };
  if (u.pathname === "/api/v1/deals/timeline") return { data: [] };
  return { data: [] };
};
const B = await roda(bundle, vazioSoUmaVez, { de: HOJE, ate: HOJE });

ok("engasgo de uma vez nao derruba a resposta", () =>
  assert.equal(B.json.ok, true, B.json.erro));

/* ---- 3) corpo que nao e JSON: a mensagem mostra o comeco do que veio ---- */
const lixo = (u) =>
  u.pathname === "/api/v1/dealFields" ? "<html>502 Bad Gateway</html>" : { data: [] };
const C = await roda(bundle, lixo, { de: HOJE, ate: HOJE });

ok("corpo ilegivel mostra o que o Pipedrive mandou", () => {
  assert.equal(C.json.ok, false);
  assert.match(C.json.erro, /corpo ileg/);
  assert.match(C.json.erro, /502 Bad Gateway/);
});

console.log(`\n${n} confer\u00eancias` + (falhou ? " \u2014 TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

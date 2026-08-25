/* A função sdr, rodando de verdade contra um Pipedrive de mentira.
   node --experimental-strip-types testes/sdr.test.mjs                        */
import { empacota, roda } from "./live-harness.mjs";
import assert from "node:assert";

const C = {
  sdr:      "966e0b1c6e28cbb30fb6d82394746d33da5c07ea",
  vendedor: "db2c9632937b836eae914bb3749d19f3b129b31d",
  lead:     "1cb9ad4729d5f241f8a329045613582070ee2c95",
  dConexao: "c527b5a136e4e64856851d721785b39b5f9274ae",
  dSql:     "7382f9db5de1930988bc7acbd676abaa4079a015",
  dOpp:     "395bf927e670b580aa5d012e9f242defca9f3050",
  dSal:     "62df15f8b5a4071a910ee37b0a4b4654afbc48db",
  leadSql:  "44a8dc2ef746c237899ea6f96f802b7b275874a2",
};
const HOJE = new Date().toISOString().slice(0, 10);
const dd = (n) => new Date(Date.parse(HOJE + "T12:00:00Z") + n * 86400e3).toISOString().slice(0, 10);
const DE = dd(-20), ATE = HOJE;

let q = 0;
const mk = (o) => Object.assign({
  id: 700 + (++q), title: "Lead " + q, status: "open", value: 15997,
  add_time: dd(-10) + " 09:00:00",
  [C.sdr]: 31, [C.vendedor]: 11, [C.lead]: 41,
}, o);

const negocios = [
  // conectado, SQL, OPS e SAL todos no período — o caminho completo
  mk({ [C.dConexao]: dd(-8), [C.dSql]: dd(-7), [C.dOpp]: dd(-6), [C.dSal]: dd(-5),
       [C.lead]: 42, [C.leadSql]: 42 }),   // veio B, ficou B — manteve
  // conectado mas parou aí
  mk({ [C.dConexao]: dd(-4), [C.sdr]: 32, [C.lead]: 42, [C.leadSql]: 41 }),  // B -> A, subiu
  // conectado e SQL, sem OPS nem SAL
  mk({ [C.dConexao]: dd(-3), [C.dSql]: dd(-2), [C.sdr]: 32, [C.lead]: 41, [C.leadSql]: 43 }), // A -> C, desceu
  /* O CASO QUE JUSTIFICA A JANELA DE 180 DIAS: criado há 5 meses, conectado há
     muito tempo, e só agora o closer aceitou. Conta como SAL do período. Com
     janela curta ele nem seria lido. */
  mk({ add_time: dd(-150) + " 09:00:00", [C.dConexao]: dd(-145), [C.dSql]: dd(-140),
       [C.dSal]: dd(-2), [C.sdr]: 31, [C.lead]: 43, status: "won" }),
  // fora do período dos dois lados — não pode entrar em conta nenhuma
  mk({ add_time: dd(-40) + " 09:00:00", [C.dConexao]: dd(-35), [C.dSql]: dd(-34) }),
  // sem SDR preenchido
  mk({ [C.dConexao]: dd(-6), [C.sdr]: null }),
];

const dublê = (u) => {
  const p = u.pathname, s = u.searchParams;
  if (p === "/api/v1/dealFields") return { data: [
    { key: C.lead, name: "Lead", options: [
      { id: 41, label: "A" }, { id: 42, label: "B" }, { id: 43, label: "C" }] },
    { key: C.leadSql, name: "Lead - SQL", options: [
      { id: 41, label: "A" }, { id: 42, label: "B" }, { id: 43, label: "C" }] },
  ] };
  if (p === "/api/v1/users") return { data: [
    { id: 11, name: "Nickolas Rocha" }, { id: 31, name: "Leticia" }, { id: 32, name: "Gabriel Frizzo" }] };
  if (p === "/api/v1/deals/timeline") {
    // a timeline filtra por add_time: só devolve o que cai na janela pedida
    const ini = s.get("start_date");
    const meses = Number(s.get("amount"));
    const f = new Date(Date.parse(ini + "T12:00:00Z"));
    f.setUTCMonth(f.getUTCMonth() + meses);
    const fim = f.toISOString().slice(0, 10);
    return { data: [{ deals: negocios.filter((d) => {
      const c = d.add_time.slice(0, 10);
      return c >= ini && c < fim;
    }) }] };
  }
  return undefined;
};

const { json, chamadas } = await roda(empacota("supabase/functions/sdr/index.ts", "sdr"),
  dublê, { de: DE, ate: ATE });

let n = 0, falhou = false;
const ok = (nome, fn) => {
  try { fn(); console.log("✅ " + nome); n++; }
  catch (e) { console.log("❌ " + nome + "\n   " + e.message); falhou = true; }
};

ok("responde ok:true", () => assert.equal(json.ok, true, json.erro));

ok("conta cada etapa pela SUA data, não pela criação", () =>
  assert.deepEqual(
    { c: json.contagem.conectados, sql: json.contagem.sql,
      ops: json.contagem.ops, sal: json.contagem.sal },
    // 704 e 705 têm SQL fora do período: entram na leitura, não na conta
    { c: 4, sql: 2, ops: 1, sal: 2 }));

ok("a janela de 180 dias alcança o lead velho que virou SAL agora", () =>
  assert.ok(json.negocios.some((d) => d.id === 704 && d.dSal === dd(-2)),
    "o negócio criado há 150 dias não foi lido"));

ok("negócio fora do período não entra em conta nenhuma", () =>
  assert.ok(!json.negocios.some((d) => d.id === 705)));

ok("só devolve quem participa de alguma etapa — não meio ano de negócios", () =>
  assert.equal(json.negocios.length, 5));

ok("o SDR vem pelo nome", () =>
  assert.deepEqual([...new Set(json.negocios.map((d) => d.sdr))].sort(),
    ["Gabriel Frizzo", "Leticia", "Sem SDR"]));

ok("a qualificação vem pelo rótulo A/B/C, não pelo id", () =>
  assert.ok(json.negocios.every((d) => d.lead === null || /^[A-F]$/.test(d.lead))));

ok("quem não tem SDR aparece agrupado, e vira aviso", () => {
  assert.ok(json.negocios.some((d) => d.sdr === "Sem SDR"));
  assert.ok(json.avisos.some((a) => /Vendedor SDR/.test(a)));
});

ok("a varredura conta o que leu", () => {
  assert.equal(json.varredura.janela_dias, 180);
  assert.ok(json.varredura.blocos >= 2, "blocos: " + json.varredura.blocos);
  assert.equal(json.varredura.truncado, false);
});

ok("não encosta na API v2 — nada de limite de 15 campos", () =>
  assert.ok(!chamadas.some((c) => c.includes("/api/v2/")), chamadas.join(" | ")));

ok("traz o lead do formulario E a requalificacao do SDR, lado a lado", () => {
  const par = (id) => { const d = json.negocios.find((x) => x.id === id); return [d.lead, d.leadSql]; };
  assert.deepEqual(par(701), ["B", "B"], "manteve");
  assert.deepEqual(par(702), ["B", "A"], "subiu");
  assert.deepEqual(par(703), ["A", "C"], "desceu");
});

console.log(`\n${n} conferências` + (falhou ? " — TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

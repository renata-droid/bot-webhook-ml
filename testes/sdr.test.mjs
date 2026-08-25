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
  /* O CASO QUE A JANELA DE CRIACAO PERDIA: criado ha 5 meses, e o closer so
     aceitou anteontem. Conta como SAL do periodo, e so aparece porque a busca
     e por quem foi MEXIDO — nao por quem foi criado. */
  mk({ add_time: dd(-150) + " 09:00:00", mexidoEm: dd(-2),
       [C.dConexao]: dd(-145), [C.dSql]: dd(-140),
       [C.dSal]: dd(-2), [C.sdr]: 31, [C.lead]: 43, status: "won" }),
  // fora do período dos dois lados — não pode entrar em conta nenhuma
  mk({ add_time: dd(-40) + " 09:00:00", mexidoEm: dd(-34),
       [C.dConexao]: dd(-35), [C.dSql]: dd(-34) }),
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
  if (p === "/api/v2/deals") {
    /* O v2 com updated_since devolve o que foi MEXIDO desde a data. O dublê
       usa `mexidoEm` de cada negócio para simular isso — inclusive o lead
       velho, criado ha meses e conectado agora. */
    const desde = (s.get("updated_since") || "").slice(0, 10);
    return { data: negocios.filter((d) => (d.mexidoEm ?? d.add_time.slice(0, 10)) >= desde),
             additional_data: {} };
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
    // 705 tem todas as datas fora do periodo: e lido e descartado
    { c: 4, sql: 2, ops: 1, sal: 2 }));

ok("o lead velho que so agora virou SAL entra", () =>
  assert.ok(json.negocios.some((d) => d.id === 704 && d.dSal === dd(-2)),
    "o negocio criado ha 150 dias nao foi lido"));

ok("nao busca por criacao: pede o que foi MEXIDO no periodo", () => {
  const v2 = chamadas.filter((c) => c.includes("/api/v2/deals"));
  assert.ok(v2.length > 0, "nenhuma chamada ao v2");
  assert.ok(v2.every((c) => c.includes("updated_since")), v2.join(" | "));
  assert.ok(!chamadas.some((c) => c.includes("timeline")), "ainda usa a timeline");
});

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
  assert.ok(json.varredura.paginas >= 1);
  assert.ok(json.varredura.brutos >= json.varredura.lidos);
  assert.equal(json.varredura.truncado, false);
});

ok("pede no maximo 15 campos customizados por chamada", () => {
  for (const c of chamadas.filter((x) => x.includes("/api/v2/deals"))) {
    const cf = new URLSearchParams(c.split("?")[1]).get("custom_fields") || "";
    assert.ok(cf.split(",").filter(Boolean).length <= 15, cf);
  }
});

ok("traz o lead do formulario E a requalificacao do SDR, lado a lado", () => {
  const par = (id) => { const d = json.negocios.find((x) => x.id === id); return [d.lead, d.leadSql]; };
  assert.deepEqual(par(701), ["B", "B"], "manteve");
  assert.deepEqual(par(702), ["B", "A"], "subiu");
  assert.deepEqual(par(703), ["A", "C"], "desceu");
});

console.log(`\n${n} conferências` + (falhou ? " — TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

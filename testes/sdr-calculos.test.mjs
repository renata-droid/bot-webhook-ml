/* A matemática da página SDR.
   node --experimental-strip-types testes/sdr-calculos.test.mjs               */
import * as N from "../lovable/calculos.ts";
import assert from "node:assert";

const f = { de: "2026-08-01", ate: "2026-08-31" };
let q = 0;
const mk = (o) => Object.assign({
  id: ++q, t: "L" + q, sdr: "Leticia", v: "Lucas", canal: "Meetime", orig: null,
  dConexao: null, dSql: null, dOpp: null, dSal: null,
  lead: null, leadSql: null, s: "open", val: 0, dCriacao: "2026-08-01",
}, o);

const rows = [
  // caminho completo, manteve a nota
  mk({ dConexao: "2026-08-02", dSql: "2026-08-02", dOpp: "2026-08-03", dSal: "2026-08-04",
       lead: "B", leadSql: "B", s: "won", val: 15000 }),
  // conectado e SQL, subiu a nota (D -> B)
  mk({ dConexao: "2026-08-05", dSql: "2026-08-05", lead: "D", leadSql: "B" }),
  // conectado e SQL, desceu (A -> C)
  mk({ dConexao: "2026-08-06", dSql: "2026-08-06", lead: "A", leadSql: "C" }),
  // só conectado
  mk({ dConexao: "2026-08-07", sdr: "Gabriel Frizzo" }),
  // lead velho: conectado em julho, mas SAL em agosto — conta como SAL do mês
  mk({ dConexao: "2026-07-10", dSql: "2026-07-10", dOpp: "2026-08-10", dSal: "2026-08-11",
       lead: "A", sdr: "Gabriel Frizzo" }),
  // tudo fora do período
  mk({ dConexao: "2026-07-01", dSql: "2026-07-01", lead: "C", leadSql: "C" }),
];

let n = 0, falhou = false;
const ok = (nome, fn) => {
  try { fn(); console.log("✅ " + nome); n++; }
  catch (e) { console.log("❌ " + nome + "\n   " + e.message); falhou = true; }
};

const fun = N.funilSdr(rows, f);

ok("cada etapa conta pela SUA data", () =>
  assert.deepEqual(
    { c: fun.conectados.length, sql: fun.sql.length, ops: fun.ops.length, sal: fun.sal.length },
    { c: 4, sql: 3, ops: 2, sal: 2 }));

ok("o lead conectado em julho e aceito em agosto e SAL de agosto", () =>
  assert.ok(fun.sal.some(d => d.dConexao === "2026-07-10")));

ok("aceite = SAL sobre OPS, e nao sobre conectados", () => {
  assert.equal(fun.aceite, 2 / 2);        // 2 SAL de 2 OPS
  assert.equal(fun.taxaGeral, 2 / 4);     // a ponta a ponta continua disponivel
});

const tab = N.porSdr(rows, f);
ok("uma linha por SDR, ordenada por SAL", () =>
  assert.deepEqual(tab.map(x => [x.sdr, x.sal]), [["Leticia", 1], ["Gabriel Frizzo", 1]]));

ok("receita conta so o que virou venda", () =>
  assert.equal(tab.find(x => x.sdr === "Leticia").receita, 15000));

const nota = N.salPorNota(rows, f);
ok("SAL repartido por nota do formulario", () => {
  assert.equal(nota.total, 2);
  assert.deepEqual(nota.porSdr.map(x => x.sdr).sort(), ["Gabriel Frizzo", "Leticia"]);
});

const req = N.requalificacao(rows, f);

ok("manteve / subiu / desceu", () =>
  assert.deepEqual(
    { m: req.time.manteve, s: req.time.subiu, d: req.time.desceu, t: req.time.total },
    { m: 1, s: 1, d: 1, t: 3 }));

ok("subir e ir para uma letra MELHOR: D -> B sobe, A -> C desce", () => {
  const sobe = req.matriz.find(l => l.de === "D").para.find(p => p.para === "B");
  const desce = req.matriz.find(l => l.de === "A").para.find(p => p.para === "C");
  assert.equal(sobe.n, 1);
  assert.equal(desce.n, 1);
});

ok("a matriz so tem linha de nota que existe", () =>
  assert.deepEqual(req.matriz.map(l => l.de).sort(), ["A", "B", "D"]));

ok("diz quantos ficaram de fora por faltar um dos lados", () =>
  // so o "so-conectado": o lead velho nem entra, o SQL dele foi em julho
  assert.equal(req.semOsDoisLados, 1));

ok("filtro por SDR corta tudo junto", () => {
  const g = N.funilSdr(rows, { ...f, sdr: "Gabriel Frizzo" });
  assert.equal(g.conectados.length, 1);
  assert.equal(g.sal.length, 1);
});

ok("os cards contam todo mundo, para bater com o Pipedrive", () => {
  const fora = [
    mk({ dConexao: "2026-08-12", dSql: "2026-08-12", dOpp: "2026-08-12", dSal: "2026-08-13",
         sdr: "Robert Rodrigues" }),
    mk({ dConexao: "2026-08-12", dOpp: "2026-08-12", sdr: "Renato Benedetti" }),
    mk({ dConexao: "2026-08-12", sdr: "" }),
  ];
  const com = N.funilSdr([...rows, ...fora], f);
  assert.equal(com.conectados.length, fun.conectados.length + 3);
  assert.equal(com.ops.length, fun.ops.length + 2);
  assert.equal(com.sal.length, fun.sal.length + 1);
});

ok("mas o detalhe por SDR so mostra quem esta na lista", () => {
  const fora = [
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "Robert Rodrigues" }),
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "Milena Bragiatto" }),
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "" }),
  ];
  assert.deepEqual(N.porSdr([...rows, ...fora], f).map(l => l.sdr).sort(),
                   ["Gabriel Frizzo", "Leticia"]);
  assert.deepEqual(N.porNota([...rows, ...fora], f, "sal").porSdr.map(l => l.sdr).sort(),
                   ["Gabriel Frizzo", "Leticia"]);
});

ok("a IA que conecta conta como SDR", () =>
  assert.equal(N.ehSdr("tecnologia@awsales.io"), true));

ok("o mesmo corte vale para a matriz de requalificacao", () => {
  const fora = mk({ dConexao: "2026-08-12", dSql: "2026-08-12",
                    lead: "A", leadSql: "B", sdr: "Milena Bragiatto" });
  const req = N.requalificacao([...rows, fora], f);
  assert.ok(!req.porSdr.some(l => l.sdr === "Milena Bragiatto"));
  assert.equal(req.time.total, N.requalificacao(rows, f).time.total);
});

ok("SQL, OPS e SAL saem da mesma conta, muda so a data", () => {
  const sql = N.porNota(rows, f, "sql"), ops = N.porNota(rows, f, "ops");
  assert.equal(sql.total, fun.sql.length);
  assert.equal(ops.total, fun.ops.length);
  assert.deepEqual(N.porNota(rows, f, "sal"), N.salPorNota(rows, f));
});

ok("acento no nome nao atrapalha a lista", () =>
  assert.equal(N.ehSdr("Letícia Almeida"), true));

ok("o que ficou de fora explica a distancia entre o card e as barras", () => {
  const fora = [
    mk({ dConexao: "2026-08-12", sdr: "Milena Bragiatto" }),
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "Renato Benedetti" }),
    mk({ dConexao: "2026-08-12", sdr: "  " }),
  ];
  const todos = [...rows, ...fora];
  const x = N.foraDaLista(todos, f);
  assert.equal(x.semCampo.conectados, 1);
  assert.equal(x.outroNome.conectados, 2);
  assert.equal(x.nomes.map(y => y.nome).sort().join(","), "Milena Bragiatto,Renato Benedetti");
  // card = soma das barras + o que ficou de fora
  const barras = N.porSdr(todos, f).reduce((a, l) => a + l.conectados, 0);
  assert.equal(N.funilSdr(todos, f).conectados.length,
               barras + x.semCampo.conectados + x.outroNome.conectados);
});

console.log(`\n${n} conferências` + (falhou ? " — TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

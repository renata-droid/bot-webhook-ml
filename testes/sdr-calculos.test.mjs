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

ok("aceite = SAL sobre conectados", () =>
  assert.equal(fun.aceite, 2 / 4));

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

ok("so quem esta na lista de SDR entra na pagina", () => {
  const fora = [
    mk({ dConexao: "2026-08-12", dSql: "2026-08-12", dSal: "2026-08-13", sdr: "Robert Rodrigues" }),
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "Allana Bueno" }),
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "Milena Bragiatto" }),
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "tecnologia@awsales.io" }),
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "" }),
  ];
  const com = N.funilSdr([...rows, ...fora], f);
  assert.deepEqual(
    { c: com.conectados.length, sal: com.sal.length },
    { c: fun.conectados.length, sal: fun.sal.length });
  assert.deepEqual(N.porSdr([...rows, ...fora], f).map(l => l.sdr).sort(),
                   ["Gabriel Frizzo", "Leticia"]);
});

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

ok("o que ficou de fora aparece separado, e fecha com o total", () => {
  const fora = [
    mk({ dConexao: "2026-08-12", sdr: "tecnologia@awsales.io" }),
    mk({ dConexao: "2026-08-12", dSal: "2026-08-13", sdr: "tecnologia@awsales.io" }),
    mk({ dConexao: "2026-08-12", sdr: "Milena Bragiatto" }),
    mk({ dConexao: "2026-08-12", sdr: "  " }),
  ];
  const todos = [...rows, ...fora];
  const f2 = N.foraDaLista(todos, f);
  assert.equal(f2.semCampo.conectados, 1);
  assert.equal(f2.outroNome.conectados, 3);
  assert.equal(f2.nomes[0].nome, "tecnologia@awsales.io");
  assert.equal(f2.nomes[0].conectados, 2);
  // 707 = 999 - 292: o de dentro mais o de fora tem que dar o total
  assert.equal(N.funilSdr(todos, f).conectados.length
             + f2.semCampo.conectados + f2.outroNome.conectados,
               todos.filter(d => d.dConexao >= f.de && d.dConexao <= f.ate).length);
});

console.log(`\n${n} conferências` + (falhou ? " — TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

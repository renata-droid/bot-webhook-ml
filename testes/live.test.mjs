/* A live nova responde igual à antiga naquilo que não devia mudar?
   node --experimental-strip-types testes/live.test.mjs                        */
import { empacota, roda } from "./live-harness.mjs";
import { execFileSync } from "node:child_process";
import { writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert";

const C = {
  vendedor:    "db2c9632937b836eae914bb3749d19f3b129b31d",
  produto:     "6621eda2196194ded0bd671ae263ccbcb213666c",
  retAgendado: "3d8b962590bb3422ffcf9ea1c2ae3223ac1745e0",
  diaReuniao:  "c8a99e668e9913e2362556c43a03bd821db81006",
};
const HOJE = new Date().toISOString().slice(0, 10);
const dd = (n) => new Date(Date.parse(HOJE + "T12:00:00Z") + n * 86400e3).toISOString().slice(0, 10);
const DE = dd(-25), ATE = HOJE;

/* Negócios abertos, todos com Vendedor. O 501 é o caso do Alexandro: o campo
   diz anteontem, a agenda diz depois de amanhã. */
const abertos = [
  { id: 501, title: "Alexandro Bianchi", status: "open", stage_id: 4, pipeline_id: 20,
    value: 26997, add_time: dd(-9) + " 09:00:00",
    [C.vendedor]: 11, [C.produto]: 21, [C.retAgendado]: dd(-2), [C.diaReuniao]: dd(-5) },
  { id: 502, title: "So o campo", status: "open", stage_id: 4, pipeline_id: 20,
    value: 15997, add_time: dd(-8) + " 09:00:00",
    [C.vendedor]: 11, [C.produto]: 21, [C.retAgendado]: dd(3), [C.diaReuniao]: dd(-6) },
  { id: 503, title: "Sem retorno nenhum", status: "open", stage_id: 3, pipeline_id: 20,
    value: 9997, add_time: dd(-7) + " 09:00:00", [C.vendedor]: 12, [C.produto]: 21 },
  { id: 504, title: "Tarefa amanha, reuniao depois", status: "open", stage_id: 4, pipeline_id: 20,
    value: 11997, add_time: dd(-6) + " 09:00:00", [C.vendedor]: 12, [C.produto]: 21 },
  { id: 505, title: "Duas reunioes fora de ordem", status: "open", stage_id: 4, pipeline_id: 20,
    value: 13997, add_time: dd(-6) + " 09:00:00", [C.vendedor]: 12, [C.produto]: 21 },
];
const ganho = { id: 601, title: "Ganhou", status: "won", stage_id: 4, pipeline_id: 20,
  value: 17997, won_time: dd(-3) + " 10:00:00", add_time: dd(-20) + " 09:00:00",
  [C.vendedor]: 11, [C.produto]: 21, [C.retAgendado]: dd(-4), [C.diaReuniao]: dd(-6) };

const atividades = [
  // a de verdade do 501: nome que não fala em retorno, e é o que manda
  { id: 9001, deal_id: 501, done: false, due_date: dd(2), type: "meeting",
    subject: "Boas Vindas Basico Aroma & ICOMM",
    conference_meeting_client: "googleMeet", conference_meeting_url: "https://meet.google.com/abc" },
  // passada e concluída: alimenta o funil, não pode virar "próxima"
  { id: 9002, deal_id: 501, done: true, due_date: dd(-5), type: "meeting",
    subject: "Reuniao", conference_meeting_client: "googleMeet" },
  { id: 9003, deal_id: 601, done: true, due_date: dd(-6), type: "meeting",
    subject: "Reuniao", conference_meeting_client: "googleMeet" },
  // reunião ganha de tarefa, mesmo sendo mais tarde
  { id: 9004, deal_id: 504, done: false, due_date: dd(1), type: "task", subject: "Mandar contrato" },
  { id: 9005, deal_id: 504, done: false, due_date: dd(6), type: "meeting", subject: "Call" },
  // entre reuniões, ganha a mais próxima — e a ordem do Pipedrive não pode mandar
  { id: 9006, deal_id: 505, done: false, due_date: dd(8), type: "meeting", subject: "Longe" },
  { id: 9007, deal_id: 505, done: false, due_date: dd(4), type: "meeting", subject: "Perto" },
];

const dublê = (u) => {
  const p = u.pathname, q = u.searchParams;
  if (p === "/api/v1/dealFields") return { data: [
    { key: C.vendedor, name: "Vendedor", options: [{ id: 11, label: "Nickolas Rocha" }, { id: 12, label: "Ellen Costa" }] },
    { key: C.produto, name: "Produto", options: [{ id: 21, label: "Consultoria" }] },
    { key: "buddy_x", name: "Buddy CS", options: [{ id: 1, label: "Allana Bueno" }, { id: 2, label: "Luis Castagne" }] },
  ] };
  if (p === "/api/v1/users")     return { data: [{ id: 11, name: "Nickolas Rocha" }] };
  if (p === "/api/v1/stages")    return { data: [
    { id: 3, name: "Proposta Enviada", pipeline_id: 20 },
    { id: 4, name: "Retorno Agendado", pipeline_id: 20 }] };
  if (p === "/api/v1/pipelines") return { data: [{ id: 20, name: "[Closers] Vendas" }] };
  if (p === "/api/v1/products")  return { data: [] };
  if (p === "/api/v1/notes")     return { data: [] };
  if (p.startsWith("/api/v1/deals/") && p.endsWith("/products")) return { data: [] };
  if (p === "/api/v1/deals/timeline")
    return { data: [{ deals: q.get("field_key") === "won_time" ? [ganho] : [] }] };
  if (p === "/api/v2/deals")
    return { data: q.get("status") === "open" ? abertos : [], additional_data: {} };
  if (p === "/api/v1/activities") {
    const ini = q.get("start_date"), fim = q.get("end_date"), soAbertas = q.get("done") === "0";
    return { data: atividades.filter((a) =>
      a.due_date >= ini && a.due_date <= fim && (!soAbertas || !a.done)), additional_data: {} };
  }
  return undefined;
};

const dir = mkdtempSync(join(tmpdir(), "live-orig-"));
const origIndex = join(dir, "index.ts");
writeFileSync(origIndex, execFileSync("git", ["show", "67463bd:supabase/functions/live/index.ts"],
  { cwd: process.cwd(), encoding: "utf8" }));

const A = await roda(empacota(origIndex, "orig"), dublê, { de: DE, ate: ATE });
const B = await roda(empacota("supabase/functions/live/index.ts", "novo"), dublê, { de: DE, ate: ATE });

let n = 0, falhou = false;
const ok = (nome, fn) => {
  try { fn(); console.log("✅ " + nome); n++; }
  catch (e) { console.log("❌ " + nome + "\n   " + e.message); falhou = true; }
};

ok("as duas versões respondem ok:true", () => {
  assert.equal(A.json.ok, true, "antiga: " + A.json.erro);
  assert.equal(B.json.ok, true, "nova: " + B.json.erro);
});

ok("contagem de negócios: idêntica", () =>
  assert.deepEqual(B.json.contagem, A.json.contagem));

ok("conferência por vendedor: idêntica", () =>
  assert.deepEqual(B.json.conferencia, A.json.conferencia));

ok("plataformas (o que alimenta 'onde a reunião aconteceu'): idêntica", () =>
  assert.deepEqual(B.json.plataformas, A.json.plataformas));

const porId = (j) => Object.fromEntries(j.deals.map((d) => [d.id, d]));
const a = porId(A.json), b = porId(B.json);

ok("os mesmos negócios, nem um a mais nem a menos", () =>
  assert.deepEqual(Object.keys(b).sort(), Object.keys(a).sort()));

ok("diaReuniao intacto em todos (é ele que faz o funil)", () =>
  assert.deepEqual(B.json.deals.map((d) => [d.id, d.diaReuniao]),
                   A.json.deals.map((d) => [d.id, d.diaReuniao])));

ok("retAgendado NÃO muda em negócio nenhum — a live só acrescenta", () =>
  assert.deepEqual(B.json.deals.map((d) => [d.id, d.retAgendado]),
                   A.json.deals.map((d) => [d.id, d.retAgendado])));

ok("o caso do Alexandro: a agenda entra como dado novo", () => {
  assert.equal(b[501].retAgendado, dd(-2), "o campo cru continua o que era");
  assert.equal(b[501].proxAtiv, dd(2), "e a agenda vem ao lado");
  assert.equal(b[501].proxAtivAssunto, "Boas Vindas Basico Aroma & ICOMM");
});

ok("sem atividade em aberto, proxAtiv vem nulo e o campo é que vale", () => {
  assert.equal(b[502].proxAtiv, null);
  assert.equal(b[502].retAgendado, dd(3));
});

ok("negócio GANHO não recebe proxAtiv", () =>
  assert.equal(b[601].proxAtiv ?? null, null));

ok("atividade concluída não vira 'próxima'", () =>
  assert.notEqual(b[501].proxAtiv, dd(-5)));

ok("reunião ganha de tarefa, mesmo sendo mais tarde", () =>
  assert.equal(b[504].proxAtiv, dd(6)));

ok("entre reuniões ganha a mais próxima, venha na ordem que vier", () =>
  assert.equal(b[505].proxAtiv, dd(4)));

ok("retorno_fonte conta certo", () =>
  assert.deepEqual(B.json.retorno_fonte,
    { pela_atividade: 3, pelo_campo: 1, sem_nada: 1, discordam: 1 }));

ok("preenchimento continua medindo o CAMPO, não a agenda", () =>
  assert.equal(B.json.preenchimento.retorno_agendado, A.json.preenchimento.retorno_agendado));

const soNovos = (j) => Object.keys(j).filter((k) => !(k in A.json));
ok("nada saiu da resposta; só entrou", () => {
  assert.deepEqual(Object.keys(A.json).filter((k) => !(k in B.json)), []);
  assert.deepEqual(soNovos(B.json).sort(), ["retorno_fonte", "varredura"]);
});

console.log(`\n${n} conferências` + (falhou ? " — TEM FALHA" : ", todas passando"));
process.exit(falhou ? 1 : 0);

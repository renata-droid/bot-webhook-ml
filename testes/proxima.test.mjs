/* node --experimental-strip-types testes/proxima.test.mjs */
import { proximaAtividade, ehReuniao } from "../supabase/functions/live/proxima.ts";
import assert from "node:assert";

const dia = (v) => (typeof v === "string" && v.length >= 10 ? v.slice(0, 10) : null);
const H = "2026-08-26";
const p = (as) => proximaAtividade(as, H, dia);
let n = 0;
const ok = (nome, fn) => { fn(); console.log("✅ " + nome); n++; };

ok("o caso do Alexandro: a atividade manda, o nome não importa", () => {
  // campo dizia 24/08; a agenda diz 26/08, num assunto que não fala em retorno
  const e = p([{ subject: "Boas Vindas Basico Aroma & ICOMM", due_date: "2026-08-26",
                 type: "meeting", conference_meeting_url: "https://meet.google.com/x" }]);
  assert.equal(e.quando, "2026-08-26");
  assert.equal(e.ehReuniao, true);
});

ok("atividade concluída não conta", () =>
  assert.equal(p([{ due_date: "2026-08-28", done: true }]), null));

ok("atividade no passado não conta", () =>
  assert.equal(p([{ due_date: "2026-08-20" }]), null));

ok("hoje conta", () =>
  assert.equal(p([{ due_date: H }]).quando, H));

ok("entre duas reuniões, ganha a mais próxima", () =>
  assert.equal(p([{ due_date: "2026-09-10", type: "meeting" },
                  { due_date: "2026-08-28", type: "meeting" }]).quando, "2026-08-28"));

ok("reunião ganha de tarefa, mesmo sendo mais tarde", () =>
  assert.equal(p([{ due_date: "2026-08-27", type: "task" },
                  { due_date: "2026-09-02", type: "meeting" }]).quando, "2026-09-02"));

ok("sem reunião nenhuma, a tarefa serve", () =>
  assert.equal(p([{ due_date: "2026-08-30", type: "task" }]).quando, "2026-08-30"));

ok("a ordem em que o Pipedrive devolve não muda o resultado", () => {
  const as = [{ due_date: "2026-09-02", type: "meeting" }, { due_date: "2026-08-27", type: "task" },
              { due_date: "2026-08-29", type: "meeting" }];
  assert.equal(p(as).quando, "2026-08-29");
  assert.equal(p([...as].reverse()).quando, "2026-08-29");
});

ok("link de vídeo vale como reunião mesmo com tipo torto", () =>
  assert.equal(ehReuniao({ type: "Reuniao de Retorno", conference_meeting_url: "https://x" }), true));

ok("agenda vazia devolve null, e aí o campo é que vale", () =>
  assert.equal(p([]), null));

console.log(`\n${n} conferências, todas passando`);

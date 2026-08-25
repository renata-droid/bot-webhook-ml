/* Roda a Edge Function inteira aqui, com um Pipedrive de mentira.
   ===============================================================
   Existe porque "eu conferi o diff" não é prova. O índice não é importável —
   tem `Deno.serve` no topo — então ele é empacotado com esbuild, o `Deno` e o
   `fetch` são trocados por dublês, e a função roda de verdade: mesma
   paginação, mesmas contas, mesma resposta JSON.

   Serve para uma coisa que nenhum outro teste daqui faz: rodar DUAS versões do
   índice sobre exatamente os mesmos dados e comparar as respostas campo a
   campo. É assim que se prova que uma mudança não mexeu no que não devia. */

import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

/** Empacota um index.ts (Deno, multi-arquivo) num .mjs que o Node importa. */
export function empacota(entrada, rotulo) {
  const dir = mkdtempSync(join(tmpdir(), "live-" + rotulo + "-"));
  const saida = join(dir, "live.mjs");
  execFileSync("npx", ["--yes", "esbuild@0.23", entrada, "--bundle",
    "--format=esm", "--platform=neutral", "--outfile=" + saida], { stdio: "pipe" });
  return saida;
}

/** Sobe a função e devolve o JSON que ela responderia para ?de=..&ate=.. */
export async function roda(bundle, pipedrive, { de, ate }) {
  let tratador = null;
  globalThis.Deno = {
    env: { get: (k) => (k === "PIPEDRIVE_API_TOKEN" ? "token-de-mentira" : undefined) },
    serve: (h) => { tratador = h; },
  };
  const chamadas = [];
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    chamadas.push(u.pathname + u.search);
    const corpo = pipedrive(u);
    if (corpo === undefined) throw new Error("endpoint sem dublê: " + u.pathname);
    // o dublê pode devolver texto cru para simular corpo vazio ou resposta torta
    const cru = corpo === "VAZIO" ? "" : typeof corpo === "string" ? corpo : JSON.stringify(corpo);
    return new Response(cru, { status: 200, headers: { "content-type": "application/json" } });
  };
  // cada import precisa de URL única, senão o Node devolve o módulo em cache
  // com o META da rodada anterior dentro
  await import(pathToFileURL(bundle).href + "?v=" + Math.random().toString(36).slice(2));
  if (!tratador) throw new Error("a função não chamou Deno.serve");
  const r = await tratador(new Request(`http://local/live?de=${de}&ate=${ate}`));
  return { json: await r.json(), chamadas };
}

export { writeFileSync };

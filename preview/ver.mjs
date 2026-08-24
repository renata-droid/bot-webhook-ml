/* Vê o painel sem Pipedrive, sem Supabase e sem login.
   ============================================================
   Existe porque quem escreve o código estava escrevendo às cegas: as
   alterações iam para a Renata sem ninguém ter olhado a tela, e cada engano
   custava uma ida e volta dela. Bloco que sumiu, cartão zerado, layout
   quebrado e erro de JavaScript aparecem aqui, antes de sair daqui.

   O que ISTO pega:  tela vazia, bloco sumido, número zerado, erro de JS.
   O que NÃO pega:   bug que só acontece com o dado real do Pipedrive.

   Uso:
     npm i playwright            (uma vez)
     node preview/ver.mjs        -> renderiza todas as páginas
     node preview/ver.mjs churn  -> só uma

   As imagens saem em preview/saida/.                                      */

import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { montaPreview, SAIDA } from "./montar.mjs";

// Blocos que precisam ter conteúdo em cada página. Vazio aqui é defeito.
const ESPERADO = {
  geral:    ["tiles", "donut", "rank", "vg-atencao", "vg-qualif"],
  retorno:  ["ret-acao", "ret-dias", "t-dias-closer", "t-ret-lista", "ret-chips"],
  churn:    ["ch-cards", "ch-qtd12", "ch-culpa", "ch-rank", "ch-buddy", "ch-produto", "ch-ret"],
  closers:  ["cl-cards", "t-hier", "t-deals"],
  reunioes: ["re-cards", "re-rank", "re-faixas", "re-dores", "re-lista"],
};

// Páginas com abas: o print da aba aberta não prova nada sobre as outras.
// O Lastro virou aba própria e ficaria fora da conferência se ninguém clicasse.
const ABAS = {
  retorno: {
    carteira: ["ret-acao", "ret-dias", "t-dias-closer", "t-ret-lista", "ret-chips"],
    lastro:   ["lastro-cards"],
    funil:    ["des-funil", "t-corte-v"],
  },
};

const so = process.argv[2];
const paginas = so ? [so] : Object.keys(ESPERADO);

mkdirSync(SAIDA, { recursive: true });
const arquivo = montaPreview();

const navegador = await chromium.launch({
  executablePath: process.env.PLAYWRIGHT_CHROMIUM || undefined,
});
const aba = await navegador.newPage({ viewport: { width: 1600, height: 1200 } });
const erros = [];
aba.on("pageerror", e => erros.push(String(e)));
// Fonte do Google e fotos do bucket não existem sem rede — é ruído esperado
// aqui, não defeito do painel. Só erro de verdade conta.
const RUIDO = /ERR_FILE_NOT_FOUND|ERR_CERT_|ERR_CONNECTION|ERR_NAME_NOT_RESOLVED|ERR_INTERNET/;
aba.on("console", m => {
  if (m.type() === "error" && !RUIDO.test(m.text())) erros.push("console: " + m.text());
});
aba.on("requestfailed", () => {});

await aba.goto("file://" + arquivo);
await aba.waitForTimeout(800);

let problemas = 0;
for (const pg of paginas) {
  await aba.click(`a[data-pg="${pg}"]`);
  await aba.waitForTimeout(500);
  await aba.screenshot({ path: join(SAIDA, pg + ".png"), fullPage: true });

  const confere = async (rotulo, ids) => {
    const vazios = [];
    for (const id of ids) {
      const n = await aba.evaluate(x => (document.getElementById(x)?.innerHTML || "").length, id);
      if (!n) vazios.push(id);
    }
    const sub = await aba.textContent("#sub");
    console.log(`${vazios.length ? "✗" : "✓"} ${rotulo.padEnd(18)} ${sub}`);
    if (vazios.length) { problemas++; console.log(`    vazios: ${vazios.join(", ")}`); }
  };

  if (ABAS[pg]) {
    for (const [nome, ids] of Object.entries(ABAS[pg])) {
      await aba.click(`#abas-ret .aba[data-aba="${nome}"]`);
      await aba.waitForTimeout(400);
      await aba.screenshot({ path: join(SAIDA, `${pg}-${nome}.png`), fullPage: true });
      await confere(`${pg}/${nome}`, ids);
    }
  } else {
    await confere(pg, ESPERADO[pg] ?? []);
  }
}

if (erros.length) { problemas++; console.log("\nerros de JS:", erros); }
console.log(problemas ? `\n${problemas} problema(s) — olhe as imagens em preview/saida/`
                      : "\nsem problemas · imagens em preview/saida/");
await navegador.close();
process.exit(problemas ? 1 : 0);

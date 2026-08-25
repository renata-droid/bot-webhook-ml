/* A matemática do Retorno bate com a tela que já está no ar?
   ============================================================
   Os outros comparadores confrontam o módulo com uma cópia da lógica antiga.
   Aqui não dá: as contas do Retorno moram DENTRO das funções que desenham a
   tela, misturadas com HTML. Copiar essa lógica para comparar seria comparar o
   módulo com a minha própria transcrição dela — provaria nada.

   Então o confronto é com a TELA. O painel é renderizado de verdade num
   navegador, com os mesmos dados falsos do preview, e os números são lidos do
   DOM. Se o módulo discordar do que está escrito na tela, é o módulo que está
   errado.

   Uso:  node --experimental-strip-types lovable/comparar-retorno.mjs           */

import { chromium } from "playwright";
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { montaPreview } from "../preview/montar.mjs";
import * as N from "./calculos.ts";

const arquivo = montaPreview();
/* O container pode trazer uma versao de Chromium diferente da que a
   playwright instalada espera. Procura a que existe de fato. */
function achaChrome() {
  if (process.env.PLAYWRIGHT_CHROMIUM) return process.env.PLAYWRIGHT_CHROMIUM;
  const raiz = process.env.PLAYWRIGHT_BROWSERS_PATH || "/opt/pw-browsers";
  for (const pasta of (existsSync(raiz) ? readdirSync(raiz) : []).sort().reverse()) {
    if (!/^chromium/.test(pasta)) continue;
    for (const bin of ["chrome-linux/chrome", "chrome-linux/headless_shell"]) {
      const c = join(raiz, pasta, bin);
      if (existsSync(c)) return c;
    }
  }
  return undefined;
}

const navegador = await chromium.launch({ executablePath: achaChrome() });
const aba = await navegador.newPage({ viewport: { width: 1600, height: 1200 } });
await aba.goto("file://" + arquivo);
await aba.waitForTimeout(800);
await aba.click('a[data-pg="retorno"]');
await aba.waitForTimeout(500);

// os mesmos dados e o mesmo recorte que a tela está usando neste instante
const { deals, state } = await aba.evaluate(() => ({ deals: D, state }));
const f = {
  de: state.de, ate: state.ate, basedata: state.basedata,
  orig: state.orig, vend: state.vend, prod: state.prod,
  canal: state.canal, lead: state.lead, temp: state.temp, ret: state.ret,
};

let ok = true;
const cmp = (nome, tela, modulo) => {
  const bate = JSON.stringify(tela) === JSON.stringify(modulo);
  console.log((bate ? "✅" : "❌") + "  " + nome);
  if (!bate) { console.log("   tela  :", JSON.stringify(tela)); console.log("   módulo:", JSON.stringify(modulo)); }
  ok = bate && ok;
};
const nums = t => (t.match(/-?[\d.]+/g) || []).map(x => Number(x.replace(/\./g, "")));

/* ---------- aba Carteira ---------- */
const cr = N.carteiraRet(deals, f);
cmp("carteira: quantos negócios em retorno",
  nums(await aba.textContent("#sub"))[0], cr.length);

const cartoesTela = await aba.$$eval("#ret-acao .stat",
  els => els.map(e => [e.querySelector(".k").textContent.trim(), e.querySelector(".v").textContent.trim()]));
const cartoes = N.cartoesRet(cr, f);
cmp("cartões: contagem dos quatro estados",
  cartoesTela.map(x => Number(x[1])), cartoes.map(c => c.n));

const dias = N.retornosPorDia(cr, f);
// o sub traz datas antes dos números; leio o trecho depois do "·" para não
// contar "24/08/2026" como se fosse contagem
const subDias = (await aba.textContent("#dias-sub")).split("·").slice(1).join("·");
cmp("retornos por dia: atrás / na janela / depois",
  nums(subDias).slice(0, 3), [dias.passado.length, dias.futuro.length, dias.depois]);

const totalTela = await aba.$$eval("#t-dias-closer tr.total td", els => els.map(e => e.textContent.trim()));
cmp("retornos por dia: linha de total (quente/morno/frio/atrasados/retornos)",
  totalTela.slice(1, 6).map(Number),
  [dias.legenda[0].n, dias.legenda[1].n, dias.legenda[2].n, dias.atrasados, dias.ag.length]);

cmp("retornos por dia: closers na tabela",
  await aba.$$eval("#t-dias-closer tbody tr:not(.total):not(.lvl3) td.name", e => e.map(x => x.textContent.trim().replace(/^[▸▾]/, ""))),
  dias.porCloser.map(c => c.v));

const lista = N.listaRet(cr, f);
cmp("lista: chips (rótulo e contagem)",
  await aba.$$eval("#ret-chips .chip", els => els.map(e =>
    [e.textContent.trim().replace(/\s+/g, " ").replace(/ R\$.*/, "").replace(/ (\d+)$/, ""), Number(e.querySelector("b").textContent)])),
  lista.chips.map(c => [c.rotulo, c.n]));

/* A etapa manda: negócio que já saiu das etapas de retorno não aparece aqui,
   mesmo com "Data Retorno Agendado" preenchida. Foi o que a Renata pegou
   conferindo contra o kanban — a tela dizia 9 onde o Pipedrive mostrava 8. */
cmp("etapa manda: negócio fora das etapas de retorno não entra na carteira",
  [], cr.filter(d => ["Link Enviado", "Proposta Enviada"].includes(d.et)).map(d => d.t));
cmp("etapa manda: nem no gráfico de retornos por dia",
  [], N.retornosPorDia(cr, f).ag.filter(d => d.id === 39001 || d.id === 39002).map(d => d.t));

/* ---------- aba Lastro ---------- */
await aba.click('#abas-ret .aba[data-aba="lastro"]');
await aba.waitForTimeout(400);
const L = N.lastro(deals, f);
cmp("lastro: reuniões / com retorno / sem nada",
  nums(await aba.textContent("#lastro-sub")).slice(-3),
  [L.reunioes.length, L.comRet.length, L.sem.length]);
cmp("lastro: closers e o placar de cada um",
  await aba.$$eval(".lastro h4", els => els.map(e => e.textContent.trim().replace(/\s+/g, " "))),
  L.porCloser.map(c => `${c.v} ${c.ok}/${c.total}`));

/* ---------- aba Funil ---------- */
await aba.click('#abas-ret .aba[data-aba="funil"]');
await aba.waitForTimeout(400);
const alvo = deals.filter(d => N.filtrosComuns(d, f));
const fun = N.cartoesFunil(alvo, f);
cmp("funil: reuniões / agendados / realizados / vendas",
  (await aba.$$eval("#des-funil .stat .v", e => e.map(x => x.textContent.trim()))).slice(0, 4).map(Number),
  [fun.reunioes.length, fun.agendados.length, fun.realizados.length, fun.ganhos.length]);

const corte = N.corteRet(alvo, f, "v");
cmp("corte por closer: nomes na ordem",
  await aba.$$eval("#t-corte-v tbody tr:not(.total) td.name", e => e.map(x => x.textContent.trim())),
  corte.linhas.map(l => l.k));
cmp("corte por closer: agendados de cada um",
  await aba.$$eval("#t-corte-v tbody tr:not(.total)", e => e.map(x => Number(x.children[2].textContent))),
  corte.linhas.map(l => l.agendados.length));

/* ---------- o caso que zerava a tela: filtrar um dia só ----------
   Filtrar [24/08 a 24/08] já derrubou a página inteira para zero. O gráfico é
   EVENTO e tem que mostrar as barras daquele dia; os cartões são ESTADO e têm
   que continuar contando a carteira inteira, vista daquele dia. Se este bloco
   passar a falhar, alguém aplicou o recorte de intervalo na carteira de novo. */
await aba.click('#abas-ret .aba[data-aba="carteira"]');
const hoje = await aba.evaluate(() => new Date().toISOString().slice(0, 10));
// pelo caminho de verdade: mexo nos campos de data como a pessoa mexe. Se o
// painel voltar a consultar o Pipedrive aqui, a tela fica em "consultando…" e
// as conferências abaixo falham — que é exatamente o que se quer travar.
await aba.fill("#f-de", hoje);
await aba.fill("#f-ate", hoje);
await aba.waitForTimeout(400);
cmp("um dia: não foi consultar o Pipedrive de novo", false,
  /consultando/i.test(await aba.textContent("#sub")));

const f1 = { ...f, de: hoje, ate: hoje };
const cr1 = N.carteiraRet(deals, f1);
cmp("um dia: a carteira NÃO encolhe", cr.length, cr1.length);

const dias1 = N.retornosPorDia(cr1, f1);
cmp("um dia: o gráfico mostra o dia, e não vazio", true, !dias1.vazio && dias1.dias.length === 1);
cmp("um dia: gráfico bate com a tela",
  Number((await aba.$$eval("#t-dias-closer tr.total td", e => e.map(x => x.textContent.trim())))[5]),
  dias1.ag.length);
cmp("um dia: os cartões continuam contando a carteira inteira",
  (await aba.$$eval("#ret-acao .stat .v", e => e.map(x => Number(x.textContent)))),
  N.cartoesRet(cr1, f1).map(c => c.n));

await aba.screenshot({ path: "preview/saida/retorno-um-dia.png", fullPage: false });

await navegador.close();
console.log(ok ? "\ntudo bate com a tela" : "\nTEM DIFERENÇA — o módulo não pode ir para o Lovable assim");
process.exit(ok ? 0 : 1);

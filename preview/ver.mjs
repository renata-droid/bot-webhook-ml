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
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(AQUI, "..");
const SAIDA = join(AQUI, "saida");

/* ---------- dados de mentira, no formato que a Edge Function devolve ----------
   Números escolhidos para parecerem a operação real: carteira com vencidos,
   retornos de hoje, no-shows, análises de call e churn. Se a tela ficar vazia
   com ISTO, ficaria vazia na vida real também. */
const FALSOS = `
const H = new Date().toISOString().slice(0,10);
const dd = n => new Date(Date.parse(H+"T12:00:00Z")+n*86400e3).toISOString().slice(0,10);
const CL = ["Lucas Gallera","Christopher","Matheus Medeiros","Nickolas Rocha","Ellen Costa"];
const BUD = ["Allana Bueno","Luis Castagne","Robert Rodrigues"];
const MOT = ["Arrependimento (comprou no impulso)","Erro de Processo (CS)",
             "Logistica ou problema e/ou marketplace","Produto do cliente","Negativa contratual"];
let q = 0;
const mk = o => Object.assign({
  id:33000+(++q), t:"Cliente "+q, v:CL[q%5], p:"Consultoria Tracao (12 encontros)",
  s:"open", val:15997, valPago:0, et:"Retorno Agendado", tmp:["Quente","Morno","Frio"][q%3],
  lead:"ABCDE"[q%5], canal:"Ligacao Meetime", orig:"ICOMM", vid:1, sdr:"Leticia",
  dCriacao:dd(-40), dDesfecho:dd(-40), dGanho:null, dPerda:null, dpar:q%20, nret:q%4,
  obj:[], cm:[], retAgendado:null, retRealizado:null, noShow:null, diaReuniao:null,
  churn:false, precoLista:19997, itens:[], reemb:0, buddy:null, saude:null, an:null,
  plataforma:null, funil:"Vendas", lm:null, dc:null,
}, o);

const deals = [];
for (let i=0;i<27;i++) deals.push(mk({ retAgendado:dd(-(1+i%19)) }));          // vencidos
for (let i=0;i<6;i++)  deals.push(mk({ retAgendado:H, diaReuniao:H }));        // hoje
for (let i=0;i<4;i++)  deals.push(mk({ noShow:dd(-2), et:"No Show" }));        // no-show
deals.push(mk({ et:"Follow UP" }));                                           // sem data
for (let i=0;i<5;i++)  deals.push(mk({ retAgendado:dd(1+i) }));                // agendados
for (let i=0;i<9;i++)  deals.push(mk({                                        // ganhos
  s:"won", dGanho:dd(-i-1), dDesfecho:dd(-i-1), et:"Ganho", valPago:15997,
  diaReuniao:dd(-i-3), retAgendado:dd(-i-2), retRealizado:dd(-i-1),
  plataforma:"Google Meet",
  an:{ nota:5+(i%5), dur:30+i, cp:50+i*3, resumo:"Lead com faturamento parado e sem trafego",
       certo:["rapport"], erro:["desconto cedo"], cond:["ancorar"], porque:"fechou" } }));
for (let i=0;i<7;i++)  deals.push(mk({                                        // perdidos
  s:"lost", dPerda:dd(-i-1), dDesfecho:dd(-i-1), et:"Perdido", diaReuniao:dd(-i-2),
  lm:["Sem orcamento","Sócios não aprovaram a compra","Parou de responder"][i%3],
  obj:[{nome:"Sem caixa",origem:"call"}],
  an:{ nota:3+(i%4), dur:20+i, cp:70+i, resumo:"Cliente sem caixa e sem urgencia",
       certo:[], erro:["monologo"], cond:[], porque:"nao fechou" } }));
for (let i=0;i<5;i++)  deals.push(mk({                                        // churn
  s:"won", dGanho:dd(-90-i*20), dDesfecho:dd(-90-i*20), et:"Ganho", valPago:15997,
  churn:true, reemb:8000+i*500, dc:dd(-(3+i*15)), saude:"Cancelado",
  buddy:BUD[i%3], cm:[MOT[i%5], MOT[(i+2)%5]] }));
deals.push(mk({ s:"open", saude:"Risco", et:"Retorno Realizado", retRealizado:dd(-1) }));

window.__painel({
  deals, periodo:{ de:dd(-23), ate:H }, geradoEm:new Date().toISOString(),
  conferencia:{ ae_ganhos:{ negocios:9, valor:143973, por_vendedor:{} } },
  preenchimento:null, contagem:{ total:deals.length }, avisos:[],
  plataformas:{ total:{"Google Meet":9}, atividades_no_periodo:120, com_link_de_video:9,
                clientes_de_video:{google_meet:9}, dominios_dos_links:{"meet.google.com":9},
                tipos_de_atividade:{meeting:40} },
  churn12: deals.filter(d=>d.churn).map(d=>({...d})),
  recebimento12: [],
});`;

function montaPreview() {
  const html = readFileSync(join(RAIZ, "painel_icomm.html"), "utf-8");
  // rindex, e não regex: um comentário DENTRO do painel cita a string
  // '<script type="module">', e uma busca ingênua casa lá e come o arquivo todo.
  const i = html.lastIndexOf('<script type="module">');
  const j = html.lastIndexOf("</script>") + "</script>".length;
  if (i < 0) throw new Error("não achei o bloco de carga do painel");
  const stub = `<script>
document.getElementById("login").style.display="none";
document.getElementById("app").style.display="grid";
document.getElementById("me-nome").textContent="Preview";
${FALSOS}
</script>`;
  const destino = join(SAIDA, "preview.html");
  writeFileSync(destino, html.slice(0, i) + stub + html.slice(j));
  return destino;
}

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

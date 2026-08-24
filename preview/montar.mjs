/* Monta o painel com dados de mentira: mesma tela, sem Pipedrive, sem Supabase
   e sem login. Mora aqui, e não dentro do ver.mjs, porque o comparador de
   números precisa exatamente da mesma página — se cada um montasse a sua, os
   dois estariam conferindo coisas diferentes e ninguém perceberia. */

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(AQUI, "..");
export const SAIDA = join(AQUI, "saida");

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
// o caso que a Renata pegou no Pipedrive: negócio que JÁ passou das etapas de
// retorno mas continua com "Data Retorno Agendado" preenchida, porque ninguém
// limpa o campo quando o negócio avança. Não pode aparecer na página Retorno.
deals.push(mk({ id:39001, t:"Passou de fase", et:"Link Enviado", retAgendado:dd(-4) }));
deals.push(mk({ id:39002, t:"Proposta com retorno", et:"Proposta Enviada", retAgendado:dd(2) }));
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

// a janela que esta "consulta" cobre — o painel usa isto para decidir se um
// filtro mais estreito precisa voltar ao Pipedrive ou só redesenhar
window.__janela = { de: dd(-23), ate: H };
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

export function montaPreview() {
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
  mkdirSync(SAIDA, { recursive: true });
  const destino = join(SAIDA, "preview.html");
  writeFileSync(destino, html.slice(0, i) + stub + html.slice(j));
  return destino;
}


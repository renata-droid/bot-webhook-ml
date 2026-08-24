import * as N from "./calc.mjs";
await import("./velho.js");
const V = globalThis.__velho;
const H = new Date().toISOString().slice(0,10);
const dd = n => new Date(Date.parse(H+"T12:00:00Z")+n*86400e3).toISOString().slice(0,10);
const CL=["Lucas Gallera","Christopher","Matheus Medeiros"];
const BUD=["Allana Bueno","Luis Castagne","Robert Rodrigues"];
const MOT=["Arrependimento (comprou no impulso)","Erro de Processo (CS)",
  "Logística ou problema e/ou marketplace","Produto do cliente","Negativa contratual",
  "Desalinhamento no comercial","Problemas pessoais do cliente"];
let q=0;
const mk=o=>Object.assign({id:++q,t:"C"+q,v:CL[q%3],p:"Prod"+(q%4),s:"open",val:15997,
 valPago:0,et:"Retorno Agendado",tmp:"Morno",lead:"B",canal:"c",orig:"ICOMM",
 dCriacao:dd(-200),dGanho:null,dPerda:null,dDesfecho:dd(-200),dpar:3,nret:1,
 retAgendado:null,retRealizado:null,noShow:null,diaReuniao:null,churn:false,reemb:0,
 dc:null,cm:[],buddy:null,saude:null,precoLista:19997,an:null},o);

const deals=[];
for(let i=0;i<20;i++) deals.push(mk({s:"won",dGanho:dd(-i-1),dDesfecho:dd(-i-1),
  valPago:i%3?15997:0,et:"Ganho"}));
for(let i=0;i<8;i++)  deals.push(mk({s:"won",dGanho:dd(-i*9-2),dDesfecho:dd(-i*9-2),
  et:"Ganho",valPago:15997,churn:true,reemb:5000+i*700,dc:dd(-(i%9)),
  buddy:BUD[i%3],cm:[MOT[i%7],MOT[(i+3)%7]],saude:"Cancelado"}));
for(let i=0;i<10;i++) deals.push(mk({s:"lost",dPerda:dd(-i),dDesfecho:dd(-i),et:"Perdido"}));

const churn12 = deals.filter(d=>d.churn).map(d=>({...d}));
const f = { de: dd(-23), ate: H, basedata:"desfecho", ret:"retorno" };
V.setD(deals); V.setState({...f, orig:"",vend:"",prod:"",canal:"",lead:"",temp:"",cba:"cancelou"});
globalThis.CHURN12 = churn12;

const rows = V.base();
const sel = N.selecaoChurn(N.base(deals,f), churn12, f, "cancelou");

const num = x => typeof x==="number" ? Number(x.toFixed(10)) : x;
const J = o => JSON.stringify(JSON.parse(JSON.stringify(o,(k,v)=>num(v))));
const cmp=(nome,a,b)=>{const ok=J(a)===J(b);console.log((ok?"✅":"❌")+"  "+nome);
  if(!ok){console.log("   velho:",J(a).slice(0,240));console.log("   novo :",J(b).slice(0,240));}return ok;};

// espelho das contas do painel antigo, feitas à mão a partir do mesmo recorte
const csV = churn12.filter(d=>d.dc && d.dc>=f.de && d.dc<=f.ate);
const ganhosV = rows.filter(d=>d.s==="won");
let ok = true;
ok = cmp("seleção: quem cancelou", csV.map(d=>d.id).sort(), sel.cs.map(d=>d.id).sort()) && ok;
ok = cmp("seleção: ganhos do período", ganhosV.map(d=>d.id).sort(), sel.ganhos.map(d=>d.id).sort()) && ok;

const rec = ganhosV.reduce((a,d)=>a+((d.valPago>0?d.valPago:d.val)||0),0);
const reembV = csV.reduce((a,d)=>a+(d.reemb||0),0);
const r = N.resumoChurn(sel.cs, sel.ganhos);
ok = cmp("resumo: reembolsado", reembV, r.reemb) && ok;
ok = cmp("resumo: recebido",    rec,    r.recebido) && ok;
ok = cmp("resumo: meta (reemb ÷ recebido)", reembV/rec, r.taxa) && ok;

const grupos = {};
csV.forEach(d=>(d.cm||[]).forEach(m=>{
  const a = ({"Arrependimento (comprou no impulso)":"Comercial","Desalinhamento no comercial":"Comercial",
    "Negativa contratual":"Comercial","Erro de Processo (CS)":"CS","Produto do cliente":"Problema do Cliente",
    "Problemas pessoais do cliente":"Problema do Cliente",
    "Logística ou problema e/ou marketplace":"Logística/Marketplace"})[m];
  grupos[a]=(grupos[a]||0)+1;}));
const c = N.culpaDoChurn(sel.cs);
ok = cmp("4 grupos: citações por área",
  Object.entries(grupos).sort(), c.linhas.map(x=>[x.nome,x.n]).sort()) && ok;

const mm = N.churnPorMes(churn12, f);
ok = cmp("média do ano = reemb ÷ meses decorridos",
  Number((mm.totReemb/mm.nMeses).toFixed(10)), Number(mm.mediaMes.toFixed(10))) && ok;
console.log("   (ano " + mm.ano + ", " + mm.nMeses + " meses, média " + N.BRL(mm.mediaMes) + "/mês)");

const cl = N.churnPorCloser(N.base(deals,f), sel.cs);
ok = cmp("closer ordenado por reembolso",
  [...cl].map(x=>x.reemb), [...cl].map(x=>x.reemb).sort((a,b)=>b-a)) && ok;

console.log(ok ? "\n✅ CHURN CONFERE" : "\n❌ divergência");
process.exit(ok?0:1);

import * as N from "./calc.mjs";
await import("./velho2.js");
const V = globalThis.__velho, V2 = globalThis.__v2;
const H = new Date().toISOString().slice(0,10);
const dd = n => new Date(Date.parse(H+"T12:00:00Z")+n*86400e3).toISOString().slice(0,10);
const CL=["Lucas Gallera","Christopher","Matheus Medeiros","Ellen Costa"];
const PR=["Consultoria Tração","Mentoria Iniciante","Digital Business"];
let q=0;
const mk=o=>Object.assign({id:++q,t:"Cliente "+q,v:CL[q%4],p:PR[q%3],s:"open",val:10000+q*137,
 valPago:0,et:"Retorno Agendado",tmp:"Morno",lead:"ABCDE"[q%5],canal:"Meetime",orig:"ICOMM",
 sdr:"Leticia",dCriacao:dd(-50),dGanho:null,dPerda:null,dDesfecho:dd(-50),dpar:3,nret:q%3,
 retAgendado:null,retRealizado:null,noShow:null,diaReuniao:null,churn:false,reemb:0,dc:null,
 cm:[],buddy:null,saude:null,precoLista:15000+q*100,an:null},o);
const deals=[];
for(let i=0;i<18;i++) deals.push(mk({s:"won",dGanho:dd(-i-1),dDesfecho:dd(-i-1),et:"Ganho",
  retAgendado:i%2?dd(-i-3):null,
  an:i%3?{nota:4+(i%6),dur:30,cp:60,lp:40,resumo:"x",certo:[],erro:[],cond:[],porque:null}:null}));
for(let i=0;i<11;i++) deals.push(mk({s:"lost",dPerda:dd(-i-1),dDesfecho:dd(-i-1),et:"Perdido",
  lm:["Sem orçamento","Fechou com outra empresa","Parou de responder"][i%3]}));
for(let i=0;i<14;i++) deals.push(mk({retAgendado:dd(-i)}));
const f={de:dd(-23),ate:H,basedata:"desfecho",ret:"retorno"};
V.setD(deals); V.setState({...f,orig:"",vend:"",prod:"",canal:"",lead:"",temp:"",busca:"",an:""});
const rows=V.base(), rowsN=N.base(deals,f);

const num=x=>typeof x==="number"?Number(x.toFixed(10)):x;
const J=o=>JSON.stringify(JSON.parse(JSON.stringify(o,(k,v)=>num(v))));
const cmp=(n,a,b)=>{const ok=J(a)===J(b);console.log((ok?"✅":"❌")+"  "+n);
 if(!ok){console.log("  velho:",J(a).slice(0,250));console.log("  novo :",J(b).slice(0,250));}return ok;};
const semRows=o=>{const{r,won,lost,churn,...x}=o;return x;};

let ok=true;
for(const v of CL){
  ok = cmp("perfilCloser · "+v, semRows(V2.perfilCloser(rows,v)), semRows(N.perfilCloser(rowsN,v))) && ok;
}
// hierarquia: mesma ordem de vendedores e produtos, mesma receita
const hN = N.hierarquia(rowsN, f);
const ordemV = [...new Set(rows.map(d=>d.v))]
  .map(v=>({v, a:V.agg(rows.filter(d=>d.v===v))}))
  .sort((x,y)=>y.a.receita-x.a.receita || y.a.opp-x.a.opp || x.v.localeCompare(y.v,"pt-BR"))
  .map(x=>[x.v, x.a.receita]);
ok = cmp("hierarquia: ordem e receita por vendedor", ordemV, hN.map(x=>[x.k,x.receita])) && ok;
ok = cmp("hierarquia: total de negócios preservado",
  rows.length, hN.reduce((a,v)=>a+v.produtos.reduce((b,p)=>b+p.negocios.length,0),0)) && ok;

for(const [b,a] of [["",""],["gallera",""],["","com"],["","8"],["","sem"],["mentoria","65"]]){
  V2.setBusca(b,a);
  ok = cmp(`filtraDeals busca="${b}" nota="${a}"`,
    V2.filtraDeals(rows).map(d=>d.id).sort(), N.filtraDeals(rowsN,b,a).map(d=>d.id).sort()) && ok;
}
console.log(ok?"\n✅ CLOSERS CONFERE":"\n❌ divergência");
process.exit(ok?0:1);

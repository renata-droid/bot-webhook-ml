import * as N from "./calc.mjs";
await import("./velho.js");
const V = globalThis.__velho;

const H = new Date().toISOString().slice(0,10);
const dd = n => new Date(Date.parse(H+"T12:00:00Z")+n*86400e3).toISOString().slice(0,10);
const CL=["Lucas Gallera","Christopher","Matheus Medeiros","Nickolas Rocha","Ellen Costa"];
let q=0;
const mk=o=>Object.assign({id:++q,t:"C"+q,v:CL[q%5],p:"Consultoria",s:"open",val:15997,
 valPago:0,et:"Retorno Agendado",tmp:["Quente","Morno","Frio"][q%3],lead:"ABCDE"[q%5],
 canal:"Meetime",orig:"ICOMM",dCriacao:dd(-40),dGanho:null,dPerda:null,dDesfecho:dd(-40),
 dpar:q%20,nret:q%4,retAgendado:null,retRealizado:null,noShow:null,diaReuniao:null,
 churn:false,reemb:0,dc:null,precoLista:19997,an:null},o);
const deals=[];
for(let i=0;i<30;i++) deals.push(mk({retAgendado:dd(-(1+i%19))}));
for(let i=0;i<12;i++) deals.push(mk({s:"won",dGanho:dd(-i-1),dDesfecho:dd(-i-1),et:"Ganho",
  retRealizado:dd(-i-2),an:{nota:5+(i%5),dur:30,cp:60,lp:40,resumo:"x",certo:[],erro:[],cond:[],porque:null}}));
for(let i=0;i<9;i++)  deals.push(mk({s:"lost",dPerda:dd(-i-1),dDesfecho:dd(-i-1),et:"Perdido"}));
for(let i=0;i<5;i++)  deals.push(mk({s:"won",dGanho:dd(-i-2),dDesfecho:dd(-i-2),et:"Ganho",
  churn:true,reemb:8000,dc:dd(-1)}));
for(let i=0;i<8;i++)  deals.push(mk({s:"open",et:"Follow UP"}));

const f = { de: dd(-23), ate: H, basedata: "desfecho", ret: "retorno" };
V.setD(deals); V.setState({ ...f, orig:"", vend:"", prod:"", canal:"", lead:"", temp:"" });

const num = x => typeof x === "number" ? Number(x.toFixed(10)) : x;
const limpa = o => JSON.parse(JSON.stringify(o, (k,v)=>num(v)));
const cmp = (nome, a, b) => {
  const x = JSON.stringify(limpa(a)), y = JSON.stringify(limpa(b));
  console.log((x===y ? "✅" : "❌") + "  " + nome);
  if (x!==y) { console.log("   velho:", x.slice(0,300)); console.log("   novo :", y.slice(0,300)); }
  return x===y;
};

let ok = true;
ok = cmp("base()  — negócios do período", V.base().length, N.base(deals,f).length) && ok;
ok = cmp("carteira() — abertos",          V.carteira().length, N.carteira(deals,f).length) && ok;
ok = cmp("agg() — TODOS os 30 campos",    V.agg(V.base()), N.agg(N.base(deals,f), f)) && ok;
ok = cmp("agg() — sobre a carteira",      V.agg(V.carteira()), N.agg(N.carteira(deals,f), f)) && ok;
ok = cmp("serie() — pontos do gráfico",   V.serie(), N.serie(deals,f)) && ok;
ok = cmp("ranking de closers",            V.ranking(V.base()), N.ranking(N.base(deals,f), f)) && ok;

// e com filtros ligados
V.setState({ vend:"Christopher" });
const f2 = { ...f, vend:"Christopher" };
ok = cmp("agg() com filtro de vendedor",  V.agg(V.base()), N.agg(N.base(deals,f2), f2)) && ok;
V.setState({ vend:"", basedata:"criacao" });
const f3 = { ...f, basedata:"criacao" };
ok = cmp("agg() por data de criação",     V.agg(V.base()), N.agg(N.base(deals,f3), f3)) && ok;

console.log(ok ? "\n✅ TODOS OS NÚMEROS BATEM" : "\n❌ divergência");
process.exit(ok?0:1);

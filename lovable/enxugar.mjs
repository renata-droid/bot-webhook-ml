/* Tira os comentários do calculos.ts para caber no limite de 60.000
   caracteres da mensagem do Lovable. Mantém o código idêntico — só some o
   que explica. Roda com: node lovable/enxugar.mjs                        */
import { readFileSync, writeFileSync } from "node:fs";

const src = readFileSync(new URL("./calculos.ts", import.meta.url), "utf8");
let out = "";
let i = 0;
/* O que veio antes decide se uma "/" abre uma regex ou é uma divisão. */
let anterior = "";

const guarda = (ch) => { out += ch; if (ch.trim()) anterior = ch; };

while (i < src.length) {
  const c = src[i], d = src[i + 1];

  if (c === "/" && d === "/") { while (i < src.length && src[i] !== "\n") i++; continue; }

  if (c === "/" && d === "*") {
    i += 2;
    while (i < src.length && !(src[i] === "*" && src[i + 1] === "/")) i++;
    i += 2;
    continue;
  }

  if (c === '"' || c === "'" || c === "`") {
    const fim = c;
    guarda(src[i++]);
    while (i < src.length) {
      if (src[i] === "\\") { out += src[i] + src[i + 1]; i += 2; continue; }
      if (src[i] === fim) { guarda(src[i++]); break; }
      out += src[i++];
    }
    continue;
  }

  /* Regex literal: só pode vir depois de operador, abre-parêntese ou vírgula. */
  if (c === "/" && "=(,:[!&|?{};+-*%~^<>".includes(anterior)) {
    guarda(src[i++]);
    let classe = false;
    while (i < src.length) {
      if (src[i] === "\\") { out += src[i] + src[i + 1]; i += 2; continue; }
      if (src[i] === "[") classe = true;
      else if (src[i] === "]") classe = false;
      else if (src[i] === "/" && !classe) { guarda(src[i++]); break; }
      out += src[i++];
    }
    while (i < src.length && /[a-z]/.test(src[i])) guarda(src[i++]);
    continue;
  }

  guarda(src[i++]);
}

/* Sobram buracos onde o comentário estava: no máximo uma linha em branco. */
out = out.split("\n").map(l => l.replace(/\s+$/, "")).join("\n")
         .replace(/\n{3,}/g, "\n\n").replace(/^\n+/, "");

const destino = new URL("./calculos-enxuto.ts", import.meta.url);
writeFileSync(destino, out);
console.log(`calculos.ts ${src.length} -> calculos-enxuto.ts ${out.length} caracteres` +
            (out.length > 60000 ? "  ⚠️  PASSOU DO LIMITE DO LOVABLE" : "  (cabe no Lovable)"));

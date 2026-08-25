Na página SDR, o bloco de AVISOS hoje só diz quantos leads estão sem o campo
"Vendedor SDR". Falta o resto: o Pipedrive conta 999 conexões no período e a
página conta 707, e a diferença some sem explicação. Vamos mostrar onde ela foi.

## 1. Acrescentar uma função em `src/lib/calculos.ts`

Cole esta função exatamente como está, logo antes de `funilSdr`. Não mexa em
mais nada do arquivo.

```ts
export function foraDaLista(rows: NegocioSdr[], f: FiltroSdr) {
  const fora = rows.filter(d => !ehSdr(d.sdr) && (!f.canal || d.canal === f.canal));
  const conta = (arr: NegocioSdr[]) => ({
    conectados: arr.filter(d => noPeriodo(d.dConexao, f)).length,
    sql: arr.filter(d => noPeriodo(d.dSql, f)).length,
    ops: arr.filter(d => noPeriodo(d.dOpp, f)).length,
    sal: arr.filter(d => noPeriodo(d.dSal, f)).length,
  });
  const preenchido = (d: NegocioSdr) => !!String(d.sdr ?? "").trim();
  const comNome = fora.filter(preenchido);
  const nomes = [...new Set(comNome.map(d => d.sdr))]
    .map(nome => ({ nome, ...conta(comNome.filter(d => d.sdr === nome)) }))
    .filter(x => x.conectados + x.sql + x.ops + x.sal > 0)
    .sort((a, b) => b.conectados - a.conectados || b.sal - a.sal);
  return {
    semCampo: conta(fora.filter(d => !preenchido(d))),
    outroNome: conta(comNome),
    nomes,
  };
}
```

## 2. Mostrar no bloco de avisos

Chame `foraDaLista(rows, filtro)` e troque o texto do aviso por duas linhas,
no mesmo estilo discreto que já está lá:

- `{semCampo.conectados} conectado(s) sem o campo "Vendedor SDR"`
- `{outroNome.conectados} conectado(s) com nome que não é de SDR: {os 3 primeiros de nomes, separados por vírgula} e mais N`

Quando o número for zero, a linha não aparece.

Embaixo das duas, uma linha só de fechamento de conta, em fonte menor:

`{conectados da página} na página + {semCampo.conectados} sem campo + {outroNome.conectados} fora da lista = {a soma} no Pipedrive`

## 3. Um errinho junto

Os avisos estão saindo com as tags `<b>` visíveis no meio do texto — o texto
está sendo renderizado como texto puro, mas vem com HTML dentro. Tire as tags
da string, o negrito faz por CSS.

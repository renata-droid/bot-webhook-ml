Três coisas.

**1.** Tire o seletor "Base da data" do topo de TODAS as páginas. O valor fica
fixo em `basedata: "desfecho"`.

**2.** Na Visão geral, o card OPP tem que contar Dia Oportunidade, igual à
página Closers — 321, não 458. Mesmo caminho de lá:

```ts
const opps = oppsNoPeriodo(deals, filtro)
const cards = resumoTime(base(deals, filtro), filtro, opps)
```

Conv. bruta passa de 9,0% para ~12,8% e a net de 8,7% para ~12,4%. É esperado.

No card OPP, troque o subtítulo `41G · 305L · 46R` por `oportunidades no
período` — esses três são desfechos, não somam mais 321, e já têm cards próprios
ao lado.

**3.** Em `src/lib/calculos.ts`, dentro da função `serie`, substitua o bloco que
monta os buckets por este, para o gráfico usar o mesmo denominador dos cards:

```ts
  const buckets = new Map<string, { opp: number; won: number; churn: number }>();
  const balde = (k: string) => {
    if (!buckets.has(k)) buckets.set(k, { opp: 0, won: 0, churn: 0 });
    return buckets.get(k)!;
  };
  const chave = (iso: string) => rotulo(new Date(iso + "T12:00:00"));

  for (const d of base(deals, f)) {
    const r = dataRef(d, f); if (!r) continue;
    const b = balde(chave(r));
    if (d.s === "won") b.won++;
    if (d.churn) b.churn++;
  }
  for (const d of oppsNoPeriodo(deals, f)) balde(chave(d.diaOpp as string)).opp++;
```

Não mexa em mais nada do arquivo.

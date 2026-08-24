/* Qual atividade representa o retorno de um negócio.
   ==================================================
   Mora num arquivo próprio para poder ser testada sem subir a função inteira.
   São seis linhas que decidem a data de todo cartão da página Retorno — o
   índice não é importável de fora (tem `Deno.serve` no topo), e regra que
   ninguém consegue rodar é regra que ninguém confere. */

export type Atividade = {
  done?: boolean;
  due_date?: string | null;
  subject?: string | null;
  type?: string | null;
  conference_meeting_url?: string | null;
  conference_meeting_client?: string | null;
};

export type Escolha = {
  quando: string;
  assunto: string | null;
  ehReuniao: boolean;
};

/* NÃO é pelo nome. O processo manda o closer escrever "Retorno" no assunto e
   ninguém escreve — o retorno do Alexandro Bianchi está agendado como "Boas
   Vindas Basico Aroma & ICOMM". Filtrar por nome ou por tipo faria um painel
   que só acerta quando todo mundo acerta, ou seja, nunca.

   Reunião ganha de tarefa, e é só isso: num negócio parado em "Retorno
   Agendado", a próxima reunião marcada é o retorno, chame-se como se chamar. */
export const ehReuniao = (a: Atividade): boolean =>
  String(a.type ?? "").toLowerCase().includes("meeting") ||
  !!a.conference_meeting_url ||
  !!a.conference_meeting_client;

/** Vale a pena trocar o candidato atual por este? */
export function melhorQue(atual: Escolha | null, cand: Escolha): boolean {
  if (!atual) return true;
  if (cand.ehReuniao !== atual.ehReuniao) return cand.ehReuniao;
  return cand.quando < atual.quando;
}

/** A próxima atividade em aberto, de hoje em diante. `null` se não houver. */
export function proximaAtividade(
  atividades: Atividade[], hoje: string, dia: (v: unknown) => string | null,
): Escolha | null {
  let melhor: Escolha | null = null;
  for (const a of atividades) {
    if (a.done) continue;
    const quando = dia(a.due_date);
    if (!quando || quando < hoje) continue;
    const cand: Escolha = { quando, assunto: a.subject ?? null, ehReuniao: ehReuniao(a) };
    if (melhorQue(melhor, cand)) melhor = cand;
  }
  return melhor;
}

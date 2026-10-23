import type { TransactionsQuery } from "@/types/market.types";

export function buildTransactionsExportUrl(
  clubId: number,
  query: TransactionsQuery,
): string {
  const params = new URLSearchParams();

  if (query.type) params.set("type", query.type);
  if (query.player_id) params.set("player_id", String(query.player_id));

  const queryText = params.toString();
  const path = `/clubs/${clubId}/transactions/export`;

  return `${process.env.NEXT_PUBLIC_API_URL}/api/v1${path}${queryText ? `?${queryText}` : ""}`;
}

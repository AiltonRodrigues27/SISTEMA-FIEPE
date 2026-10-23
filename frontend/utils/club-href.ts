import type { TransactionsQuery } from "@/types/market.types";

export type ClubTab = "squad" | "lineup" | "history";

type ClubHrefOptions = TransactionsQuery & { tab?: ClubTab };

export function buildClubHref(clubId: number, options: ClubHrefOptions = {}) {
  const params = new URLSearchParams();

  if (options.tab && options.tab !== "squad") params.set("tab", options.tab);
  if (options.type) params.set("type", options.type);
  if (options.player_id) params.set("player_id", String(options.player_id));

  const query = params.toString();
  return query ? `/clubs/${clubId}?${query}` : `/clubs/${clubId}`;
}

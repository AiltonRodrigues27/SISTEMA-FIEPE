import { z } from "zod";
import type { TransactionsQuery } from "@/types/market.types";
import type { RawSearchParams } from "@/types/search-params.types";
import type { ClubTab } from "@/utils/club-href";

const transactionTypeSchema = z.enum(["COMPRA", "VENDA"]);
const playerIdSchema = z.coerce.number().int().min(1);

function firstValue(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export function parseTransactionsFilters(
  raw: RawSearchParams,
): TransactionsQuery {
  const types = (firstValue(raw.type) ?? "").split(",").flatMap((text) => {
    const parsed = transactionTypeSchema.safeParse(text);
    return parsed.success ? [parsed.data] : [];
  });
  const playerId = playerIdSchema.safeParse(firstValue(raw.player_id));

  return {
    type: types.length === 1 ? types[0] : undefined,
    player_id: playerId.success ? playerId.data : undefined,
  };
}

export function parseClubTab(raw: string | string[] | undefined): ClubTab {
  const tab = firstValue(raw);

  return tab === "history" || tab === "lineup" ? tab : "squad";
}

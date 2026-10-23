import { z } from "zod";
import type { PlayersQuery } from "@/types/players.types";
import type { RawSearchParams } from "@/types/search-params.types";

export const PLAYERS_PAGE_SIZE = 10;

const optionalInt = (min: number, max: number) =>
  z.coerce.number().int().min(min).max(max).optional().catch(undefined);

const optionalDecimal = (min: number, max: number) =>
  z.coerce.number().min(min).max(max).optional().catch(undefined);

// Todo campo tem `catch`: um valor inválido na URL é ignorado em vez de quebrar a tela.
const playersFiltersSchema = z.object({
  search: z.string().trim().min(2).max(100).optional().catch(undefined),
  position: z
    .enum(["GOL", "ZAG", "LAT", "MEI", "ATA"])
    .optional()
    .catch(undefined),
  condition: z
    .enum(["APTO", "MAL_CONDICIONADO", "DOENTE"])
    .optional()
    .catch(undefined),
  free: z
    .enum(["true", "false"])
    .transform((value) => value === "true")
    .optional()
    .catch(undefined),
  club_id: optionalInt(1, 2147483647),
  min_age: optionalInt(16, 45),
  max_age: optionalInt(16, 45),
  min_value: optionalDecimal(0, 550),
  max_value: optionalDecimal(0, 550),
  sort: z
    .enum([
      "name",
      "value_asc",
      "value_desc",
      "age_asc",
      "age_desc",
      "position",
    ])
    .optional()
    .catch(undefined),
  page: z.coerce.number().int().min(1).catch(1),
});

export function parsePlayersFilters(raw: RawSearchParams): PlayersQuery {
  const firstValues = Object.fromEntries(
    Object.entries(raw).map(([key, value]) => [
      key,
      Array.isArray(value) ? value[0] : value,
    ]),
  );
  const filters = playersFiltersSchema.parse(firstValues);

  // A API recusa "só livres" junto com clube (400): a tela nunca envia os dois.
  return filters.free === true ? { ...filters, club_id: undefined } : filters;
}

import type { ApiResult } from "@/types/api.types";
import type { PlayersPage, PlayersQuery } from "@/types/players.types";
import { api } from "@/utils/api";
import { toApiError } from "@/utils/api-error";

export async function getPlayers(
  params: PlayersQuery,
): Promise<ApiResult<PlayersPage>> {
  try {
    const response = await api.get<PlayersPage>("/players", { params });

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

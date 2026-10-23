import type { ApiResult } from "@/types/api.types";
import type {
  CreatePlayerBody,
  Player,
  PlayerCondition,
  PlayersPage,
  PlayersQuery,
  UpdatePlayerBody,
} from "@/types/players.types";
import { api } from "@/lib/api";
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

export async function createPlayer(
  body: CreatePlayerBody,
): Promise<ApiResult<Player>> {
  try {
    const response = await api.post<Player>("/players", body);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function updatePlayer(
  playerId: number,
  body: UpdatePlayerBody,
): Promise<ApiResult<Player>> {
  try {
    const response = await api.put<Player>(`/players/${playerId}`, body);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function changePlayerCondition(
  playerId: number,
  condition: PlayerCondition,
): Promise<ApiResult<Player>> {
  try {
    const response = await api.patch<Player>(`/players/${playerId}/condition`, {
      condition,
    });

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function deletePlayer(playerId: number): Promise<ApiResult<null>> {
  try {
    await api.delete(`/players/${playerId}`);

    return { ok: true, data: null };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

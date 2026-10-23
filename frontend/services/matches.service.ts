import type { ApiResult } from "@/types/api.types";
import type {
  MatchDetail,
  MatchSummary,
  PlayMatchBody,
} from "@/types/matches.types";
import { api } from "@/lib/api";
import { toApiError } from "@/utils/api-error";

export async function getMatches(
  clubId?: number,
): Promise<ApiResult<MatchSummary[]>> {
  try {
    const response = await api.get<MatchSummary[]>("/matches", {
      params: { club_id: clubId },
    });

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function getMatch(
  matchId: number,
): Promise<ApiResult<MatchDetail>> {
  try {
    const response = await api.get<MatchDetail>(`/matches/${matchId}`);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function playMatch(
  body: PlayMatchBody,
): Promise<ApiResult<MatchDetail>> {
  try {
    const response = await api.post<MatchDetail>("/matches", body);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

import type { ApiResult } from "@/types/api.types";
import type { MatchSummary } from "@/types/matches.types";
import { api } from "@/utils/api";
import { toApiError } from "@/utils/api-error";

export async function getMatches(): Promise<ApiResult<MatchSummary[]>> {
  try {
    const response = await api.get<MatchSummary[]>("/matches");

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

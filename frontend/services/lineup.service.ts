import type { ApiResult } from "@/types/api.types";
import type { Lineup, SetLineupBody } from "@/types/league.types";
import { api } from "@/lib/api";
import { toApiError } from "@/utils/api-error";

export async function getLineup(clubId: number): Promise<ApiResult<Lineup>> {
  try {
    const response = await api.get<Lineup>(`/clubs/${clubId}/lineup`);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function setLineup(
  clubId: number,
  body: SetLineupBody,
): Promise<ApiResult<Lineup>> {
  try {
    const response = await api.put<Lineup>(`/clubs/${clubId}/lineup`, body);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

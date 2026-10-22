import type { ApiResult } from "@/types/api.types";
import type { StandingRow } from "@/types/standings.types";
import { api } from "@/utils/api";
import { toApiError } from "@/utils/api-error";

export async function getStandings(): Promise<ApiResult<StandingRow[]>> {
  try {
    const response = await api.get<StandingRow[]>("/standings");

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

import type { ApiResult } from "@/types/api.types";
import type { Club } from "@/types/clubs.types";
import { api } from "@/utils/api";
import { toApiError } from "@/utils/api-error";

export async function getClubs(): Promise<ApiResult<Club[]>> {
  try {
    const response = await api.get<Club[]>("/clubs");

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

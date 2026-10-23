import type { ApiResult } from "@/types/api.types";
import type {
  Club,
  ClubDetail,
  ClubSort,
  CreateClubBody,
} from "@/types/clubs.types";
import { api } from "@/lib/api";
import { toApiError } from "@/utils/api-error";

export async function getClubs(sort?: ClubSort): Promise<ApiResult<Club[]>> {
  try {
    const response = await api.get<Club[]>("/clubs", { params: { sort } });

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function getClub(clubId: number): Promise<ApiResult<ClubDetail>> {
  try {
    const response = await api.get<ClubDetail>(`/clubs/${clubId}`);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function createClub(
  body: CreateClubBody,
): Promise<ApiResult<Club>> {
  try {
    const response = await api.post<Club>("/clubs", body);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

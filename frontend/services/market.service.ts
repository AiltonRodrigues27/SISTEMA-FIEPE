import type { ApiResult } from "@/types/api.types";
import type {
  BuyPlayerBody,
  Purchase,
  Sale,
  TransactionHistory,
  TransactionsQuery,
} from "@/types/market.types";
import { api } from "@/lib/api";
import { toApiError } from "@/utils/api-error";

export async function buyPlayer(
  playerId: number,
  body: BuyPlayerBody,
): Promise<ApiResult<Purchase>> {
  try {
    const response = await api.post<Purchase>(`/players/${playerId}/buy`, body);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function sellPlayer(playerId: number): Promise<ApiResult<Sale>> {
  try {
    const response = await api.post<Sale>(`/players/${playerId}/sell`);

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

export async function getClubTransactions(
  clubId: number,
  query: TransactionsQuery,
): Promise<ApiResult<TransactionHistory>> {
  try {
    const response = await api.get<TransactionHistory>(
      `/clubs/${clubId}/transactions`,
      { params: query },
    );

    return { ok: true, data: response.data };
  } catch (error) {
    return { ok: false, ...toApiError(error) };
  }
}

"use server";

import { buyPlayerSchema } from "@/schemas/purchase.schema";
import { buyPlayer, sellPlayer } from "@/services/market.service";
import type { ActionResultWithData } from "@/types/action.types";
import type { Purchase, Sale } from "@/types/market.types";
import {
  INVALID_FIELDS_MESSAGE,
  getFirstErrorOfEachField,
} from "@/utils/field-errors";

export async function buyPlayerAction(
  playerId: number,
  formData: FormData,
): Promise<ActionResultWithData<Purchase>> {
  const parsed = buyPlayerSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return {
      ok: false,
      message: INVALID_FIELDS_MESSAGE,
      fieldErrors: getFirstErrorOfEachField(parsed.error),
    };
  }

  const result = await buyPlayer(playerId, parsed.data);
  if (!result.ok) {
    return {
      ok: false,
      message: result.message,
      isNetworkError: result.status === null,
    };
  }

  return { ok: true, message: "Jogador comprado", data: result.data };
}

export async function sellPlayerAction(
  playerId: number,
): Promise<ActionResultWithData<Sale>> {
  const result = await sellPlayer(playerId);
  if (!result.ok) return { ok: false, message: result.message };

  return { ok: true, message: "Jogador vendido", data: result.data };
}

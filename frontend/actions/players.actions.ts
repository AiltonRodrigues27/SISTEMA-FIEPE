"use server";

import { revalidatePath } from "next/cache";
import {
  createPlayerSchema,
  playerConditionSchema,
  updatePlayerSchema,
} from "@/schemas/player.schema";
import {
  changePlayerCondition,
  createPlayer,
  deletePlayer,
  updatePlayer,
} from "@/services/players.service";
import type { ActionResult, ActionResultWithData } from "@/types/action.types";
import type { Player } from "@/types/players.types";
import {
  INVALID_FIELDS_MESSAGE,
  getFirstErrorOfEachField,
} from "@/utils/field-errors";

export async function createPlayerAction(
  formData: FormData,
): Promise<ActionResultWithData<Player>> {
  const parsed = createPlayerSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return {
      ok: false,
      message: INVALID_FIELDS_MESSAGE,
      fieldErrors: getFirstErrorOfEachField(parsed.error),
    };
  }

  const result = await createPlayer(parsed.data);
  if (!result.ok) return { ok: false, message: result.message };

  revalidatePath("/", "layout");
  return { ok: true, message: "Jogador cadastrado", data: result.data };
}

export async function updatePlayerAction(
  playerId: number,
  formData: FormData,
): Promise<ActionResult> {
  const parsed = updatePlayerSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return {
      ok: false,
      message: INVALID_FIELDS_MESSAGE,
      fieldErrors: getFirstErrorOfEachField(parsed.error),
    };
  }

  const result = await updatePlayer(playerId, parsed.data);
  if (!result.ok) return { ok: false, message: result.message };

  revalidatePath("/", "layout");
  return { ok: true, message: "Jogador atualizado." };
}

export async function changePlayerConditionAction(
  playerId: number,
  formData: FormData,
): Promise<ActionResultWithData<Player>> {
  const parsed = playerConditionSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return {
      ok: false,
      message: INVALID_FIELDS_MESSAGE,
      fieldErrors: getFirstErrorOfEachField(parsed.error),
    };
  }

  const result = await changePlayerCondition(playerId, parsed.data.condition);
  if (!result.ok) return { ok: false, message: result.message };

  revalidatePath("/", "layout");
  return { ok: true, message: "Condição alterada", data: result.data };
}

export async function deletePlayerAction(
  playerId: number,
): Promise<ActionResult> {
  const result = await deletePlayer(playerId);
  if (!result.ok) return { ok: false, message: result.message };

  revalidatePath("/", "layout");
  return { ok: true, message: "Jogador excluído" };
}

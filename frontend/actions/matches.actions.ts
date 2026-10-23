"use server";

import { revalidatePath } from "next/cache";
import { playMatchSchema } from "@/schemas/lineup.schema";
import { playMatch } from "@/services/matches.service";
import type { ActionResultWithData } from "@/types/action.types";
import type { PlayedMatch } from "@/types/matches.types";
import { getFirstErrorOfEachField } from "@/utils/field-errors";

export async function playMatchAction(
  formData: FormData,
): Promise<ActionResultWithData<PlayedMatch>> {
  const parsed = playMatchSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return {
      ok: false,
      message: "Escolha o mandante e o visitante.",
      fieldErrors: getFirstErrorOfEachField(parsed.error),
    };
  }

  const result = await playMatch(parsed.data);
  if (!result.ok) return { ok: false, message: result.message };

  revalidatePath("/", "layout");
  return {
    ok: true,
    message: "Partida jogada",
    data: {
      matchId: result.data.id,
      home: result.data.home,
      away: result.data.away,
    },
  };
}

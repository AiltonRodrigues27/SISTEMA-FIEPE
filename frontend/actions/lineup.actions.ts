"use server";

import { revalidatePath } from "next/cache";
import { lineupSchema } from "@/schemas/lineup.schema";
import { setLineup } from "@/services/lineup.service";
import type { ActionResultWithData } from "@/types/action.types";
import type { Lineup } from "@/types/league.types";
import { getFirstErrorOfEachField } from "@/utils/field-errors";

export async function setLineupAction(
  clubId: number,
  formData: FormData,
): Promise<ActionResultWithData<Lineup>> {
  const parsed = lineupSchema.safeParse({
    formation: formData.get("formation"),
    player_ids: formData.getAll("player_ids"),
  });
  if (!parsed.success) {
    return {
      ok: false,
      message: Object.values(getFirstErrorOfEachField(parsed.error))[0],
    };
  }

  const result = await setLineup(clubId, parsed.data);
  if (!result.ok) return { ok: false, message: result.message };

  revalidatePath("/", "layout");
  return { ok: true, message: "Escalação salva", data: result.data };
}

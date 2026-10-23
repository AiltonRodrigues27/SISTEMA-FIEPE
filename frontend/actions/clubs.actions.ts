"use server";

import { revalidatePath } from "next/cache";
import { createClubSchema } from "@/schemas/club.schema";
import { createClub } from "@/services/clubs.service";
import type { ActionResultWithData } from "@/types/action.types";
import type { Club } from "@/types/clubs.types";
import {
  INVALID_FIELDS_MESSAGE,
  getFirstErrorOfEachField,
} from "@/utils/field-errors";

export async function createClubAction(
  formData: FormData,
): Promise<ActionResultWithData<Club>> {
  const parsed = createClubSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return {
      ok: false,
      message: INVALID_FIELDS_MESSAGE,
      fieldErrors: getFirstErrorOfEachField(parsed.error),
    };
  }

  const result = await createClub(parsed.data);
  if (!result.ok) return { ok: false, message: result.message };

  revalidatePath("/", "layout");
  return { ok: true, message: "Clube criado", data: result.data };
}

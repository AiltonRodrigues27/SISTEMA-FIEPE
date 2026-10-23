import { z } from "zod";

export const createClubSchema = z.object({
  name: z
    .string()
    .trim()
    .min(3, "Use de 3 a 60 caracteres.")
    .max(60, "Use de 3 a 60 caracteres."),
  acronym: z
    .string()
    .trim()
    .length(3, "Use exatamente 3 letras.")
    .transform((value) => value.toUpperCase()),
});

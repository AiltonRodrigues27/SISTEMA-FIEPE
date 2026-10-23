import { z } from "zod";

export const lineupSchema = z.object({
  formation: z.enum(["3-1", "2-2", "2-1-1", "1-2-1"], {
    error: "Escolha a formação.",
  }),
  player_ids: z
    .array(z.coerce.number().int().min(1))
    .length(5, "Escolha um titular para cada uma das 5 vagas.")
    .refine((ids) => new Set(ids).size === ids.length, {
      error: "Cada titular só pode ocupar uma vaga.",
    }),
});

export const playMatchSchema = z.object({
  home_club_id: z.coerce
    .number({ error: "Escolha o mandante." })
    .int()
    .min(1, "Escolha o mandante."),
  away_club_id: z.coerce
    .number({ error: "Escolha o visitante." })
    .int()
    .min(1, "Escolha o visitante."),
});

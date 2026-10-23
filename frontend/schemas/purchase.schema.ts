import { z } from "zod";
import { toApiDateTime } from "@/utils/format";

export const buyPlayerSchema = z.object({
  club_id: z.coerce
    .number({ error: "Escolha o clube." })
    .int("Escolha o clube.")
    .min(1, "Escolha o clube."),
  loyalty_until: z
    .string()
    .min(1, "Informe o fim da fidelidade.")
    .transform(toApiDateTime),
});

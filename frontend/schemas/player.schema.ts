import { z } from "zod";

const NAME_MESSAGE = "Use de 3 a 100 caracteres.";
const ATTRIBUTE_MESSAGE = "Use um valor de 1 a 99.";

const rangedInt = (min: number, max: number, message: string) =>
  z.preprocess(
    (value) => (value === "" ? undefined : value),
    z.coerce
      .number({ error: message })
      .int(message)
      .min(min, message)
      .max(max, message),
  );

export const updatePlayerSchema = z.object({
  name: z.string().trim().min(3, NAME_MESSAGE).max(100, NAME_MESSAGE),
  position: z.enum(["GOL", "ZAG", "LAT", "MEI", "ATA"], {
    error: "Escolha uma posição.",
  }),
  age: rangedInt(16, 45, "Use uma idade de 16 a 45 anos."),
  agility: rangedInt(1, 100, "Use um valor de 1 a 100."),
});

export const createPlayerSchema = updatePlayerSchema.extend({
  pace: rangedInt(1, 99, ATTRIBUTE_MESSAGE),
  shooting: rangedInt(1, 99, ATTRIBUTE_MESSAGE),
  passing: rangedInt(1, 99, ATTRIBUTE_MESSAGE),
  dribbling: rangedInt(1, 99, ATTRIBUTE_MESSAGE),
  defending: rangedInt(1, 99, ATTRIBUTE_MESSAGE),
  physical: rangedInt(1, 99, ATTRIBUTE_MESSAGE),
  potential: rangedInt(1, 99, "Informe o potencial, de 1 a 99."),
});

export const playerConditionSchema = z.object({
  condition: z.enum(["APTO", "MAL_CONDICIONADO", "DOENTE"], {
    error: "Escolha uma condição.",
  }),
});

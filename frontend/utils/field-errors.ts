import { z } from "zod";

export const INVALID_FIELDS_MESSAGE = "Corrija os campos destacados.";

export function getFirstErrorOfEachField(
  error: z.ZodError,
): Record<string, string> {
  const { fieldErrors } = z.flattenError(error);

  return Object.fromEntries(
    Object.entries(fieldErrors).flatMap(([field, messages]) =>
      messages?.[0] ? [[field, messages[0]]] : [],
    ),
  );
}

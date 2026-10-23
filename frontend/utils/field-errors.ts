import { z } from "zod";

export const INVALID_FIELDS_MESSAGE = "Corrija os campos destacados.";

export function getFirstErrorOfEachField(
  error: z.ZodError,
): Record<string, string> {
  const firstErrors: Record<string, string> = {};

  for (const issue of error.issues) {
    if (issue.path.length === 0) continue;

    const field = String(issue.path[0]);
    if (!Object.hasOwn(firstErrors, field)) firstErrors[field] = issue.message;
  }

  return firstErrors;
}

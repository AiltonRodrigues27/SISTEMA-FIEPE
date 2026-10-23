import { isAxiosError } from "axios";
import type { ApiError } from "@/types/api.types";

const NETWORK_ERROR_MESSAGE =
  "Não foi possível falar com a API. Verifique a conexão e tente de novo.";
const UNEXPECTED_ERROR_MESSAGE = "A API devolveu um erro inesperado.";

export function toApiError(error: unknown): ApiError {
  // Se não veio do axios, é bug do código e não pode ser engolido.
  if (!isAxiosError<{ message?: string }>(error)) throw error;

  if (!error.response) {
    return { status: null, message: NETWORK_ERROR_MESSAGE };
  }

  return {
    status: error.response.status,
    message: error.response.data?.message ?? UNEXPECTED_ERROR_MESSAGE,
  };
}

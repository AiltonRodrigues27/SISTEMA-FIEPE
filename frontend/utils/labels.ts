import type { PlayerCondition, PlayerPosition } from "@/types/players.types";

export const POSITION_LABELS: Record<PlayerPosition, string> = {
  GOL: "Goleiro",
  ZAG: "Zagueiro",
  LAT: "Lateral",
  MEI: "Meio-campo",
  ATA: "Atacante",
};

export const CONDITION_LABELS: Record<PlayerCondition, string> = {
  APTO: "Apto",
  MAL_CONDICIONADO: "Mal condicionado",
  DOENTE: "Doente",
};

export const ATTRIBUTE_LABELS: Record<string, string> = {
  shooting: "Finalização",
  passing: "Passe",
  dribbling: "Drible",
  defending: "Defesa",
};

// O valor vem da URL e pode não ser uma chave válida; por isso a conferência.
export function findLabel(
  labels: Record<string, string>,
  key: string,
): string | undefined {
  return Object.hasOwn(labels, key) ? labels[key] : undefined;
}

export const MATCH_RESULT_LABELS = {
  MANDANTE: "Vitória do mandante",
  VISITANTE: "Vitória do visitante",
  EMPATE: "Empate",
} as const;

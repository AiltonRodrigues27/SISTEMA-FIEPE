import type { Formation, LineupSlot } from "@/types/league.types";
import type { PlayerPosition } from "@/types/players.types";

type FormationShape = { defense: number; midfield: number; attack: number };

export const FORMATION_SHAPES: Record<Formation, FormationShape> = {
  "3-1": { defense: 3, midfield: 0, attack: 1 },
  "2-2": { defense: 2, midfield: 0, attack: 2 },
  "2-1-1": { defense: 2, midfield: 1, attack: 1 },
  "1-2-1": { defense: 1, midfield: 2, attack: 1 },
};

export const FORMATIONS: Formation[] = ["3-1", "2-2", "2-1-1", "1-2-1"];

export function describeFormation(formation: Formation): string {
  const { defense, midfield, attack } = FORMATION_SHAPES[formation];
  const parts = [`Defesa ${defense}`];
  if (midfield > 0) parts.push(`meio ${midfield}`);
  parts.push(`ataque ${attack}`);

  return parts.join(", ");
}

function buildSlots(
  count: number,
  prefix: string,
  label: string,
  positions: PlayerPosition[],
): LineupSlot[] {
  return Array.from({ length: count }, (_, index) => ({
    key: `${prefix}-${index}`,
    label,
    positions,
  }));
}

export function buildLineupSlots(formation: Formation): LineupSlot[] {
  const shape = FORMATION_SHAPES[formation];

  return [
    ...buildSlots(1, "gk", "Goleiro", ["GOL"]),
    ...buildSlots(shape.defense, "df", "Defesa", ["ZAG", "LAT"]),
    ...buildSlots(shape.midfield, "mf", "Meio", ["MEI"]),
    ...buildSlots(shape.attack, "at", "Ataque", ["ATA"]),
  ];
}

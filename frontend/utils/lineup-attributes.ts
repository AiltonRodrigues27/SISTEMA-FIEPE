import type { UsedAttribute } from "@/types/league.types";
import type { Player, PlayerPosition } from "@/types/players.types";
import { ATTRIBUTE_LABELS } from "@/utils/labels";

const POSITION_ORDER: PlayerPosition[] = ["GOL", "ZAG", "LAT", "MEI", "ATA"];

const ATTACK_ATTRIBUTE = {
  ZAG: "dribbling",
  LAT: "dribbling",
  MEI: "passing",
  ATA: "shooting",
} as const;

function compareSquadOrder(a: Player, b: Player): number {
  return (
    POSITION_ORDER.indexOf(a.position) - POSITION_ORDER.indexOf(b.position) ||
    a.name.localeCompare(b.name, "pt-BR") ||
    a.id - b.id
  );
}

// Na partida os jogadores de linha seguem a ordem do elenco (posição e nome),
// não a ordem das vagas; só dá para saber a ordem real com as 4 vagas cheias.
export function getLineIndexes(linePlayers: (Player | undefined)[]): number[] {
  const chosen = linePlayers.filter(
    (player): player is Player => player !== undefined,
  );
  if (chosen.length < linePlayers.length) {
    return linePlayers.map((_, index) => index + 1);
  }

  const inSquadOrder = [...chosen].sort(compareSquadOrder);
  return chosen.map((player) => inSquadOrder.indexOf(player) + 1);
}

// RN20: o 1º de linha só defende, o 2º ataca e defende, o 3º e o 4º só atacam;
// o goleiro só defende.
export function getUsedAttributes(
  player: Player,
  lineIndex: number | null,
): UsedAttribute[] {
  const defense = {
    label: ATTRIBUTE_LABELS.defending,
    value: player.defending,
  };
  if (player.position === "GOL" || lineIndex === 1) return [defense];

  const attackKey = ATTACK_ATTRIBUTE[player.position];
  const attack = {
    label: ATTRIBUTE_LABELS[attackKey],
    value: player[attackKey],
  };
  return lineIndex === 2 ? [attack, defense] : [attack];
}

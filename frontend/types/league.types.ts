import type { Player, PlayerPosition } from "@/types/players.types";

export type Formation = "3-1" | "2-2" | "2-1-1" | "1-2-1";

export type Lineup = {
  club_id: number;
  formation: Formation | null;
  complete: boolean;
  players: Player[];
};

export type SetLineupBody = {
  formation: Formation;
  player_ids: number[];
};

export type LineupSlot = {
  key: string;
  label: string;
  positions: PlayerPosition[];
};

export type UsedAttribute = { label: string; value: number };

export type LineupRow = {
  slot: LineupSlot;
  selectedId: string | null;
  player: Player | undefined;
  options: { value: string; label: string }[];
  attributes: UsedAttribute[];
};

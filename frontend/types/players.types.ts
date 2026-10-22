export type PlayerPosition = "GOL" | "ZAG" | "LAT" | "MEI" | "ATA";
export type PlayerCondition = "APTO" | "MAL_CONDICIONADO" | "DOENTE";

export type Player = {
  id: number;
  name: string;
  position: PlayerPosition;
  agility: number;
  age: number;
  condition: PlayerCondition;
  base_value: number;
  market_value: number;
  pace: number;
  shooting: number;
  passing: number;
  dribbling: number;
  defending: number;
  physical: number;
  potential: number;
  overall: number;
  club_id: number | null;
};

export type PageMeta = {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
};

export type PlayersPage = {
  data: Player[];
  meta: PageMeta;
};

export type PlayersQuery = {
  free?: boolean;
  limit?: number;
};

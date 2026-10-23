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

export type CreatePlayerBody = {
  name: string;
  position: PlayerPosition;
  agility: number;
  age: number;
  pace: number;
  shooting: number;
  passing: number;
  dribbling: number;
  defending: number;
  physical: number;
  potential: number;
};

export type UpdatePlayerBody = Pick<
  CreatePlayerBody,
  "name" | "position" | "agility" | "age"
>;

export type PlayerSort =
  "name" | "value_asc" | "value_desc" | "age_asc" | "age_desc" | "position";

export type PlayersQuery = {
  search?: string;
  position?: PlayerPosition;
  condition?: PlayerCondition;
  free?: boolean;
  club_id?: number;
  min_age?: number;
  max_age?: number;
  min_value?: number;
  max_value?: number;
  sort?: PlayerSort;
  page?: number;
  limit?: number;
};

export type PlayerFormValues = Record<string, string>;

export type AttributeScore = number | null | "invalid";

export type PlayerAction = "edit" | "condition" | "buy";

export type PlayerDialogName = PlayerAction | "details" | "delete";

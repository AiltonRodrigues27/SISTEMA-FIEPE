import type { Player } from "@/types/players.types";

export type Club = {
  id: number;
  name: string;
  acronym: string;
  cash: number;
  squad_value: number;
  net_worth: number;
};

export type ClubOption = Pick<Club, "id" | "name" | "acronym" | "cash">;

export type ClubSort = "name" | "net_worth_asc" | "net_worth_desc";

export type CreateClubBody = {
  name: string;
  acronym: string;
};

export type Contract = {
  purchase_value: number;
  loyalty_until: string;
  remaining_days: number;
  penalty_rate: number;
};

export type SquadMember = Player & {
  contract: Contract | null;
};

export type ClubDetail = Club & {
  players: SquadMember[];
};

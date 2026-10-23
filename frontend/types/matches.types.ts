export type MatchSide = {
  club_id: number;
  club_name: string;
  formation: string;
  goals: number;
};

export type MatchResult = "MANDANTE" | "VISITANTE" | "EMPATE";

export type MatchSummary = {
  id: number;
  played_at: string;
  home: MatchSide;
  away: MatchSide;
  result: MatchResult;
};

export type DuelPlayer = {
  player_id: number;
  player_name: string;
  position: string;
  condition: string;
  attribute: string;
  value: number;
};

export type Duel = {
  order: number;
  attacking_club_id: number;
  attacker: DuelPlayer;
  defender: DuelPlayer;
  goal: boolean;
};

export type MatchDetail = MatchSummary & {
  duels: Duel[];
};

export type PlayMatchBody = {
  home_club_id: number;
  away_club_id: number;
};

export type PlayedMatch = { matchId: number; home: MatchSide; away: MatchSide };

export type TeamSide = "home" | "away";

export type PitchPlayer = {
  id: number;
  name: string;
  position: string;
  condition: string;
  line: 1 | 2 | 3 | 4 | null;
  attack?: { attribute: string; value: number; scored: boolean };
  defense?: number;
};

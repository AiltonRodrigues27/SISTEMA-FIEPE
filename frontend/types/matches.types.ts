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

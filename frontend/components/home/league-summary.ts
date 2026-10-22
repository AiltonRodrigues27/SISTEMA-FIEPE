import { getClubs } from "@/services/clubs.service";
import { getMatches } from "@/services/matches.service";
import { getPlayers } from "@/services/players.service";
import { getStandings } from "@/services/standings.service";

export type LeagueSummary = {
  playersTotal: number;
  freePlayersTotal: number;
  clubsTotal: number;
  matchesTotal: number;
  leader: { clubName: string; points: number } | null;
};

// Devolve null se qualquer chamada falhar: a tela inicial funciona sem os números.
export async function loadLeagueSummary(): Promise<LeagueSummary | null> {
  const [players, freePlayers, clubs, matches, standings] = await Promise.all([
    getPlayers({ limit: 1 }),
    getPlayers({ free: true, limit: 1 }),
    getClubs(),
    getMatches(),
    getStandings(),
  ]);

  if (
    !players.ok ||
    !freePlayers.ok ||
    !clubs.ok ||
    !matches.ok ||
    !standings.ok
  ) {
    return null;
  }

  // A API já devolve a classificação ordenada: a primeira linha é o líder.
  const leaderRow = matches.data.length > 0 ? standings.data[0] : undefined;

  return {
    playersTotal: players.data.meta.total_items,
    freePlayersTotal: freePlayers.data.meta.total_items,
    clubsTotal: clubs.data.length,
    matchesTotal: matches.data.length,
    leader: leaderRow
      ? { clubName: leaderRow.club_name, points: leaderRow.points }
      : null,
  };
}

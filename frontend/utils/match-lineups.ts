import type {
  DuelPlayer,
  MatchDetail,
  PitchPlayer,
} from "@/types/matches.types";

// RN20: os 3 ataques de um time, em ordem, partem do 4º, do 3º e do 2º jogador
// de linha; quem defende são o goleiro (null), o 1º e o 2º jogador de linha.
const ATTACKER_LINES = [4, 3, 2] as const;
const DEFENDER_LINES = [null, 1, 2] as const;

// Os 5 titulares de um clube aparecem nos 6 duelos: quem ataca nos duelos do
// próprio clube e quem defende nos duelos do adversário.
export function buildTeamLineup(
  match: MatchDetail,
  clubId: number,
): PitchPlayer[] {
  const players = new Map<number, PitchPlayer>();
  const duels = [...match.duels].sort((a, b) => a.order - b.order);
  const ownAttacks = duels.filter((duel) => duel.attacking_club_id === clubId);
  const opponentAttacks = duels.filter(
    (duel) => duel.attacking_club_id !== clubId,
  );

  function getPlayer(player: DuelPlayer, line: PitchPlayer["line"]) {
    const existing = players.get(player.player_id);
    if (existing) return existing;

    const created: PitchPlayer = {
      id: player.player_id,
      name: player.player_name,
      position: player.position,
      condition: player.condition,
      line,
    };
    players.set(player.player_id, created);
    return created;
  }

  ownAttacks.forEach((duel, index) => {
    getPlayer(duel.attacker, ATTACKER_LINES[index]).attack = {
      attribute: duel.attacker.attribute,
      value: duel.attacker.value,
      scored: duel.goal,
    };
  });
  opponentAttacks.forEach((duel, index) => {
    getPlayer(duel.defender, DEFENDER_LINES[index]).defense =
      duel.defender.value;
  });

  return [...players.values()];
}

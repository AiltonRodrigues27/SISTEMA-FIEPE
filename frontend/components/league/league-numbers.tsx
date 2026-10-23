import { CircleCheck, Shield, Swords, UserRound, Users } from "lucide-react";
import { getClubs } from "@/services/clubs.service";
import { getMatches } from "@/services/matches.service";
import { getPlayers } from "@/services/players.service";
import { pluralize } from "@/utils/format";

export async function LeagueNumbers() {
  const [players, freePlayers, clubs, matches] = await Promise.all([
    getPlayers({ limit: 1 }),
    getPlayers({ free: true, limit: 1 }),
    getClubs(),
    getMatches(),
  ]);

  const counters =
    players.ok && freePlayers.ok && clubs.ok && matches.ok
      ? [
          {
            icon: Users,
            value: players.data.meta.total_items,
            label: pluralize(
              players.data.meta.total_items,
              "jogador",
              "jogadores",
            ),
          },
          {
            icon: UserRound,
            value: freePlayers.data.meta.total_items,
            label: pluralize(
              freePlayers.data.meta.total_items,
              "livre",
              "livres",
            ),
          },
          {
            icon: Shield,
            value: clubs.data.length,
            label: pluralize(clubs.data.length, "clube", "clubes"),
          },
          {
            icon: Swords,
            value: matches.data.length,
            label: pluralize(matches.data.length, "partida", "partidas"),
          },
        ]
      : [];

  return (
    <ul className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-caption">
      {counters.map(({ icon: Icon, value, label }) => (
        <li key={label} className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <Icon className="size-3.5 text-muted-foreground" aria-hidden />
            <span className="font-medium">{value}</span>
            <span className="text-muted-foreground">{label}</span>
          </span>
          <span aria-hidden className="size-[3px] rounded-full bg-border" />
        </li>
      ))}
      <li className="flex items-center gap-1.5 text-muted-foreground">
        <CircleCheck className="size-3.5" aria-hidden />
        Não precisa de login
      </li>
    </ul>
  );
}

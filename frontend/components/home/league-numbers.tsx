import { CircleCheck, Shield, Swords, UserRound, Users } from "lucide-react";
import type { LeagueSummary } from "@/components/home/league-summary";
import { pluralize } from "@/utils/format";

type LeagueNumbersProps = {
  summaryPromise: Promise<LeagueSummary | null>;
};

export async function LeagueNumbers({ summaryPromise }: LeagueNumbersProps) {
  const summary = await summaryPromise;

  const counters = summary
    ? [
        {
          icon: Users,
          value: summary.playersTotal,
          label: pluralize(summary.playersTotal, "jogador", "jogadores"),
        },
        {
          icon: UserRound,
          value: summary.freePlayersTotal,
          label: pluralize(summary.freePlayersTotal, "livre", "livres"),
        },
        {
          icon: Shield,
          value: summary.clubsTotal,
          label: pluralize(summary.clubsTotal, "clube", "clubes"),
        },
        {
          icon: Swords,
          value: summary.matchesTotal,
          label: pluralize(summary.matchesTotal, "partida", "partidas"),
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

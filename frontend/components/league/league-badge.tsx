import { getMatches } from "@/services/matches.service";
import { getStandings } from "@/services/standings.service";
import { pluralize } from "@/utils/format";

export async function LeagueBadge() {
  const [matches, standings] = await Promise.all([
    getMatches(),
    getStandings(),
  ]);

  if (!matches.ok || !standings.ok) return null;

  // A API já devolve a classificação ordenada: a primeira linha é o líder.
  const leader = matches.data.length > 0 ? standings.data[0] : undefined;

  const leaderText = leader
    ? `líder: ${leader.club_name}, ${leader.points} ${pluralize(leader.points, "ponto", "pontos")}`
    : "nenhuma partida ainda";

  return (
    <div className="flex items-center gap-2 rounded-full border bg-background py-1.25 pr-3 pl-2.5 text-caption">
      <span aria-hidden className="size-2 rounded-full bg-success" />
      <span className="font-medium">Liga Fictícia 2026</span>
      <span aria-hidden className="text-muted-foreground">
        ·
      </span>
      <span className="text-muted-foreground">{leaderText}</span>
    </div>
  );
}

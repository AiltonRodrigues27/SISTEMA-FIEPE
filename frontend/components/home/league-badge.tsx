import type { LeagueSummary } from "@/components/home/league-summary";
import { pluralize } from "@/utils/format";

type LeagueBadgeProps = {
  summaryPromise: Promise<LeagueSummary | null>;
};

export async function LeagueBadge({ summaryPromise }: LeagueBadgeProps) {
  const summary = await summaryPromise;

  if (!summary) return null;

  const leaderText = summary.leader
    ? `líder: ${summary.leader.clubName}, ${summary.leader.points} ${pluralize(summary.leader.points, "ponto", "pontos")}`
    : "nenhuma partida ainda";

  return (
    <div className="flex items-center gap-2 rounded-full border bg-background py-[5px] pr-3 pl-2.5 text-caption">
      <span aria-hidden className="size-2 rounded-full bg-success" />
      <span className="font-medium">Liga Fictícia 2026</span>
      <span aria-hidden className="text-muted-foreground">
        ·
      </span>
      <span className="text-muted-foreground">{leaderText}</span>
    </div>
  );
}

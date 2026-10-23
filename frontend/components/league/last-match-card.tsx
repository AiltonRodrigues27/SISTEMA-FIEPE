import { ChevronRight } from "lucide-react";
import Link from "next/link";
import { MatchScoreboard } from "@/components/league/match-scoreboard";
import { Button } from "@/components/ui/button";
import type { MatchSummary } from "@/types/matches.types";

type LastMatchCardProps = {
  match: MatchSummary;
  acronyms: Map<number, string>;
};

export function LastMatchCard({ match, acronyms }: LastMatchCardProps) {
  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-body-sm text-muted-foreground">Última partida</h2>
      <div className="flex flex-col gap-4 rounded-xl border bg-card p-4 shadow-xs sm:flex-row sm:items-center">
        <div className="flex-1">
          <MatchScoreboard match={match} acronyms={acronyms} />
        </div>
        <Button
          variant="outline"
          nativeButton={false}
          render={<Link href={`/matches/${match.id}`} />}
        >
          Ver duelos
          <ChevronRight aria-hidden />
        </Button>
      </div>
    </section>
  );
}

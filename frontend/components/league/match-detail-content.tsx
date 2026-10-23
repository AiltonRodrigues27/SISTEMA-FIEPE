import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DuelsTable } from "@/components/league/duels-table";
import { MatchPitch } from "@/components/league/match-pitch";
import { MatchScoreboard } from "@/components/league/match-scoreboard";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { getClubs } from "@/services/clubs.service";
import { getMatch } from "@/services/matches.service";

type MatchDetailContentProps = {
  params: Promise<{ id: string }>;
};

export async function MatchDetailContent({ params }: MatchDetailContentProps) {
  const { id } = await params;
  const matchId = Number(id);
  if (!Number.isInteger(matchId) || matchId < 1) notFound();

  const [result, clubs] = await Promise.all([getMatch(matchId), getClubs()]);
  if (!result.ok) {
    if (result.status === 404) notFound();
    return (
      <ErrorState
        title="Não foi possível carregar a partida"
        message={result.message}
      />
    );
  }

  const match = result.data;
  const acronyms = new Map(
    (clubs.ok ? clubs.data : []).map((club) => [club.id, club.acronym]),
  );

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        className="self-start"
        nativeButton={false}
        render={<Link href="/matches" />}
      >
        <ArrowLeft aria-hidden />
        Voltar para partidas
      </Button>
      <h1 className="sr-only">
        {match.home.club_name} {match.home.goals} × {match.away.goals}{" "}
        {match.away.club_name}
      </h1>
      <section className="rounded-xl border bg-card p-5 shadow-xs">
        <MatchScoreboard match={match} acronyms={acronyms} withFormation />
      </section>
      <MatchPitch match={match} />
      <DuelsTable match={match} acronyms={acronyms} />
    </>
  );
}

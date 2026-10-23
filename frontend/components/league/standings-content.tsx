import { ListOrdered } from "lucide-react";
import {
  RecentMatchesCard,
  TableOrderCard,
} from "@/components/league/standings-side-cards";
import { StandingsTable } from "@/components/league/standings-table";
import { EmptyState } from "@/components/shared/empty-state";
import { ListSection } from "@/components/shared/list-section";
import { getClubs } from "@/services/clubs.service";
import { getMatches } from "@/services/matches.service";
import { getStandings } from "@/services/standings.service";

export async function StandingsContent() {
  const [standings, clubs, matches] = await Promise.all([
    getStandings(),
    getClubs(),
    getMatches(),
  ]);

  const acronyms = new Map(
    (clubs.ok ? clubs.data : []).map((club) => [club.id, club.acronym]),
  );

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_18rem] lg:items-start">
      <ListSection
        result={standings}
        errorTitle="Não foi possível carregar a classificação"
        isEmpty={(rows) => rows.length === 0}
        empty={
          <EmptyState
            icon={ListOrdered}
            title="Nenhum clube cadastrado"
            description="A classificação mostra todos os clubes, mesmo os que ainda não jogaram."
          />
        }
      >
        {(rows) => (
          <>
            <StandingsTable rows={rows} acronyms={acronyms} />
            <p className="border-t px-4 py-3 text-caption text-muted-foreground">
              J: jogos · V: vitórias · E: empates · D: derrotas · GP: gols pró ·
              GC: gols contra · SG: saldo de gols · Pts: pontos
            </p>
          </>
        )}
      </ListSection>
      <div className="flex flex-col gap-4">
        <RecentMatchesCard matches={matches.ok ? matches.data : []} />
        <TableOrderCard />
      </div>
    </div>
  );
}

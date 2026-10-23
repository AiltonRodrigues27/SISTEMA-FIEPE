import { Swords } from "lucide-react";
import { LastMatchCard } from "@/components/league/last-match-card";
import { MatchesClubFilter } from "@/components/league/matches-club-filter";
import { MatchesTable } from "@/components/league/matches-table";
import { NewMatchAction } from "@/components/league/new-match-action";
import { EmptyState } from "@/components/shared/empty-state";
import { ListSection } from "@/components/shared/list-section";
import { getClubs } from "@/services/clubs.service";
import { getMatches } from "@/services/matches.service";
import type { RawSearchParams } from "@/types/search-params.types";
import { pluralize } from "@/utils/format";

type MatchesContentProps = {
  searchParams: Promise<RawSearchParams>;
};

function parseClubId(raw: string | string[] | undefined): number | undefined {
  const parsed = Number(Array.isArray(raw) ? raw[0] : raw);

  return Number.isInteger(parsed) && parsed > 0 ? parsed : undefined;
}

export async function MatchesContent({ searchParams }: MatchesContentProps) {
  const rawParams = await searchParams;
  const clubId = parseClubId(rawParams.club_id);
  const [matches, clubs, allMatches] = await Promise.all([
    getMatches(clubId),
    getClubs(),
    clubId === undefined ? null : getMatches(),
  ]);

  const clubList = clubs.ok ? clubs.data : [];
  const acronyms = new Map(clubList.map((club) => [club.id, club.acronym]));
  const latest = allMatches ?? matches;
  const lastMatch = latest.ok ? latest.data[0] : undefined;

  return (
    <>
      {lastMatch && <LastMatchCard match={lastMatch} acronyms={acronyms} />}
      <ListSection
        result={matches}
        errorTitle="Não foi possível carregar as partidas"
        isEmpty={(list) => list.length === 0 && clubId === undefined}
        empty={
          <EmptyState
            icon={Swords}
            title="Nenhuma partida jogada"
            description="Escale os 5 titulares de dois clubes e jogue a primeira partida. O resultado aparece aqui e na classificação."
            action={<NewMatchAction variant="outline" />}
          />
        }
      >
        {(list) => (
          <>
            <div className="flex flex-wrap items-center justify-between gap-3 p-4">
              <div className="flex flex-col gap-1">
                <h2 className="text-heading-card">Histórico de partidas</h2>
                <p className="text-caption text-muted-foreground">
                  Da mais recente para a mais antiga.
                </p>
              </div>
              <MatchesClubFilter clubId={clubId} clubs={clubList} />
            </div>
            {list.length === 0 ? (
              <EmptyState
                icon={Swords}
                title="Nenhuma partida deste clube"
                description="Esse clube ainda não jogou. Escolha outro clube ou jogue uma partida."
              />
            ) : (
              <>
                <MatchesTable matches={list} acronyms={acronyms} />
                <p className="border-t px-4 py-3 text-caption text-muted-foreground">
                  {list.length} {pluralize(list.length, "partida", "partidas")}
                </p>
              </>
            )}
          </>
        )}
      </ListSection>
    </>
  );
}

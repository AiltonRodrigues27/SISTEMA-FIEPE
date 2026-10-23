import { SearchX, Users, X } from "lucide-react";
import Link from "next/link";
import { NewPlayerButton } from "@/components/players/new-player-button";
import { PlayersFilters } from "@/components/players/players-filters";
import { PlayersPagination } from "@/components/players/players-pagination";
import { PlayersTable } from "@/components/players/players-table";
import { PlayersToolbar } from "@/components/players/players-toolbar";
import { EmptyState } from "@/components/shared/empty-state";
import { ListSection } from "@/components/shared/list-section";
import { Button } from "@/components/ui/button";
import {
  PLAYERS_PAGE_SIZE,
  parsePlayersFilters,
} from "@/schemas/players-filters.schema";
import { getClubs } from "@/services/clubs.service";
import { getLineup } from "@/services/lineup.service";
import { getPlayers } from "@/services/players.service";
import type { Player } from "@/types/players.types";
import type { RawSearchParams } from "@/types/search-params.types";

type PlayersContentProps = {
  searchParams: Promise<RawSearchParams>;
};

// A tela avisa ao deixar um titular doente; por isso precisa saber quem são
// os titulares dos clubes que aparecem na página.
async function getStarterIds(players: Player[]): Promise<number[]> {
  const clubIds = new Set(
    players.flatMap(({ club_id }) => (club_id === null ? [] : [club_id])),
  );
  const lineups = await Promise.all([...clubIds].map(getLineup));

  return lineups.flatMap((lineup) =>
    lineup.ok ? lineup.data.players.map(({ id }) => id) : [],
  );
}

export async function PlayersContent({ searchParams }: PlayersContentProps) {
  const rawParams = await searchParams;
  const filters = parsePlayersFilters(rawParams);

  const countFilters = {
    ...filters,
    free: undefined,
    page: undefined,
    sort: undefined,
    limit: 1,
  };
  // A API recusa "livres" junto com clube; com clube escolhido não há livres.
  const hasClubFilter = filters.club_id !== undefined;

  const [players, clubs, allCount, freeCount, clubCount] = await Promise.all([
    getPlayers({ ...filters, limit: PLAYERS_PAGE_SIZE }),
    getClubs(),
    getPlayers(countFilters),
    hasClubFilter ? null : getPlayers({ ...countFilters, free: true }),
    getPlayers({ ...countFilters, free: false }),
  ]);

  const counts =
    allCount.ok && clubCount.ok && (freeCount === null || freeCount.ok)
      ? {
          all: allCount.data.meta.total_items,
          free: freeCount === null ? 0 : freeCount.data.meta.total_items,
          club: clubCount.data.meta.total_items,
        }
      : null;

  const clubList = clubs.ok ? clubs.data : [];
  const starterIds = players.ok ? await getStarterIds(players.data.data) : [];
  const hasFilters = Object.entries(filters).some(
    ([key, value]) =>
      value !== undefined && !["page", "sort", "limit"].includes(key),
  );

  const emptyState = hasFilters ? (
    <EmptyState
      icon={SearchX}
      title={`Nenhum jogador encontrado${filters.search ? ` para “${filters.search}”` : ""}`}
      description="Confira a grafia ou tire alguns filtros. A busca ignora maiúsculas, minúsculas e acentos."
      action={
        <Button
          variant="outline"
          nativeButton={false}
          render={<Link href="/players" />}
        >
          <X aria-hidden />
          Limpar filtros
        </Button>
      }
    />
  ) : (
    <EmptyState
      icon={Users}
      title="Nenhum jogador cadastrado"
      description="Com o banco recém-criado, a lista começa vazia."
      action={<NewPlayerButton variant="outline" />}
    />
  );

  return (
    <>
      <PlayersFilters clubs={clubList} />
      <ListSection
        result={players}
        errorTitle="Não foi possível carregar os jogadores"
        isEmpty={(page) => page.data.length === 0}
        empty={emptyState}
      >
        {(page) => (
          <>
            <PlayersToolbar counts={counts} />
            <PlayersTable
              players={page.data}
              clubs={clubList}
              starterIds={starterIds}
            />
            <PlayersPagination meta={page.meta} searchParams={rawParams} />
          </>
        )}
      </ListSection>
      <p className="text-caption text-muted-foreground">
        Overall e valor de mercado são calculados a cada consulta. A busca
        ignora maiúsculas, minúsculas e acentos.
      </p>
    </>
  );
}

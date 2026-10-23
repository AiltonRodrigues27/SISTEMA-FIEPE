import { Shirt, ShoppingCart, Users } from "lucide-react";
import Link from "next/link";
import { ClubHeader } from "@/components/clubs/club-header";
import { ClubNotFound } from "@/components/clubs/club-not-found";
import { ClubSummaryCards } from "@/components/clubs/club-summary-cards";
import { ClubTabs } from "@/components/clubs/club-tabs";
import { SquadCard } from "@/components/clubs/squad-card";
import { LineupTab } from "@/components/league/lineup-tab";
import { ClubHistory } from "@/components/market/club-history";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { ListCard } from "@/components/shared/list-card";
import { ListSection } from "@/components/shared/list-section";
import { Button } from "@/components/ui/button";
import {
  parseClubTab,
  parseTransactionsFilters,
} from "@/schemas/transactions-filters.schema";
import { getClub } from "@/services/clubs.service";
import { getLineup } from "@/services/lineup.service";
import { getClubTransactions } from "@/services/market.service";
import type { RawSearchParams } from "@/types/search-params.types";

const SQUAD_LIMIT = 12;
const FREE_PLAYERS_HREF = "/players?free=true";

type ClubDetailContentProps = {
  params: Promise<{ id: string }>;
  searchParams: Promise<RawSearchParams>;
};

export async function ClubDetailContent({
  params,
  searchParams,
}: ClubDetailContentProps) {
  const { id } = await params;
  const rawParams = await searchParams;
  const clubId = Number(id);
  if (!Number.isInteger(clubId) || clubId < 1) return <ClubNotFound />;

  const [clubResult, history] = await Promise.all([
    getClub(clubId),
    getClubTransactions(clubId, {}),
  ]);
  if (!clubResult.ok) {
    if (clubResult.status === 404) return <ClubNotFound />;
    return (
      <ErrorState
        title="Não foi possível carregar o clube"
        message={clubResult.message}
      />
    );
  }

  const club = clubResult.data;
  const tab = parseClubTab(rawParams.tab);
  // A venda avisa quando o jogador é titular, então a escalação é lida junto.
  const lineup = tab === "history" ? null : await getLineup(clubId);
  const starterIds = lineup?.ok ? lineup.data.players.map(({ id }) => id) : [];

  return (
    <>
      <ClubHeader
        club={club}
        squadLimit={SQUAD_LIMIT}
        actions={
          <Button
            nativeButton={false}
            render={<Link href={FREE_PLAYERS_HREF} />}
          >
            <ShoppingCart aria-hidden />
            Comprar jogadores
          </Button>
        }
      />
      <ClubSummaryCards
        club={club}
        squadCount={club.players.length}
        squadLimit={SQUAD_LIMIT}
      />
      <div className="border-b">
        <ClubTabs
          clubId={club.id}
          tab={tab}
          squadCount={club.players.length}
          historyCount={history.ok ? history.data.data.length : undefined}
        />
      </div>
      {tab === "lineup" && lineup ? (
        <LineupTab
          clubId={club.id}
          clubName={club.name}
          squad={club.players}
          lineup={lineup}
        />
      ) : tab === "history" ? (
        <ListSection
          result={history}
          errorTitle="Não foi possível carregar o histórico"
          errorHint="Os totais e a exportação ficam indisponíveis até a lista carregar."
        >
          {(data) => (
            <ClubHistory
              clubId={club.id}
              filters={parseTransactionsFilters(rawParams)}
              history={data}
            />
          )}
        </ListSection>
      ) : (
        <ListCard>
          {club.players.length === 0 ? (
            <EmptyState
              icon={Shirt}
              title="Nenhum jogador no elenco"
              description={`Compre jogadores livres para montar o elenco. O limite é de ${SQUAD_LIMIT} jogadores, e o custo de cada compra não pode passar de 50% do caixa.`}
              action={
                <Button
                  variant="outline"
                  nativeButton={false}
                  render={<Link href={FREE_PLAYERS_HREF} />}
                >
                  <Users aria-hidden />
                  Ver jogadores livres
                </Button>
              }
            />
          ) : (
            <SquadCard
              squad={club.players}
              clubName={club.name}
              starterIds={starterIds}
            />
          )}
        </ListCard>
      )}
    </>
  );
}

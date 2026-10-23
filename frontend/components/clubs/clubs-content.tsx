import { Shield } from "lucide-react";
import { ClubsSortSelect } from "@/components/clubs/clubs-sort-select";
import { ClubsTable } from "@/components/clubs/clubs-table";
import { NewClubButton } from "@/components/clubs/new-club-button";
import { EmptyState } from "@/components/shared/empty-state";
import { ListSection } from "@/components/shared/list-section";
import { Badge } from "@/components/ui/badge";
import { parseClubSort } from "@/schemas/clubs-sort.schema";
import { getClubs } from "@/services/clubs.service";
import type { RawSearchParams } from "@/types/search-params.types";
import { pluralize } from "@/utils/format";

const MAX_CLUBS = 20;

type ClubsContentProps = {
  searchParams: Promise<RawSearchParams>;
};

export async function ClubsContent({ searchParams }: ClubsContentProps) {
  const rawParams = await searchParams;
  const sort = parseClubSort(rawParams.sort);
  const clubs = await getClubs(sort);

  return (
    <ListSection
      result={clubs}
      errorTitle="Não foi possível carregar os clubes"
      isEmpty={(list) => list.length === 0}
      empty={
        <EmptyState
          icon={Shield}
          title="Nenhum clube cadastrado"
          description="Crie o primeiro clube com nome e sigla. Ele começa com 300,00 em caixa e sem jogadores."
          action={<NewClubButton variant="outline" />}
        />
      }
    >
      {(list) => (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3 p-4">
            <div className="flex items-center gap-2">
              <p className="text-body-sm font-medium">
                {list.length} {pluralize(list.length, "clube", "clubes")}
              </p>
              <Badge variant="secondary">
                {list.length} de {MAX_CLUBS}
              </Badge>
            </div>
            <ClubsSortSelect sort={sort} />
          </div>
          <ClubsTable clubs={list} />
          <p className="border-t px-4 py-3 text-caption text-muted-foreground">
            Clubes pelo nome por padrão ou pelo patrimônio, do maior para o
            menor, com empate desfeito pelo nome.
          </p>
        </>
      )}
    </ListSection>
  );
}

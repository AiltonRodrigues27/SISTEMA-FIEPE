import { Swords } from "lucide-react";
import { Suspense } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { MatchesContent } from "@/components/league/matches-content";
import { MatchesLoading } from "@/components/league/matches-loading";
import { NewMatchAction } from "@/components/league/new-match-action";
import { PageHeader } from "@/components/shared/page-header";
import type { RawSearchParams } from "@/types/search-params.types";

type MatchesPageProps = {
  searchParams: Promise<RawSearchParams>;
};

export default function MatchesPage({ searchParams }: MatchesPageProps) {
  return (
    <AppShell>
      <PageHeader
        icon={Swords}
        title="Partidas"
        description="Jogue partidas entre clubes com os 5 titulares escalados e acompanhe o histórico."
        actions={
          <Suspense fallback={null}>
            <NewMatchAction />
          </Suspense>
        }
      />
      <Suspense fallback={<MatchesLoading />}>
        <MatchesContent searchParams={searchParams} />
      </Suspense>
    </AppShell>
  );
}

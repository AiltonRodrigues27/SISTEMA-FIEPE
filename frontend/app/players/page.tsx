import { Users } from "lucide-react";
import { Suspense } from "react";
import { NewPlayerButton } from "@/components/players/new-player-button";
import { PlayersContent } from "@/components/players/players-content";
import { PlayersLoading } from "@/components/players/players-loading";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/shared/page-header";
import type { RawSearchParams } from "@/types/search-params.types";

type PlayersPageProps = {
  searchParams: Promise<RawSearchParams>;
};

export default function PlayersPage({ searchParams }: PlayersPageProps) {
  return (
    <AppShell>
      <PageHeader
        icon={Users}
        title="Jogadores"
        description="Cadastre jogadores, acompanhe os indicadores e compre os que estão livres."
        actions={<NewPlayerButton />}
      />
      <Suspense fallback={<PlayersLoading />}>
        <PlayersContent searchParams={searchParams} />
      </Suspense>
    </AppShell>
  );
}

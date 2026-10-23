import { ListOrdered } from "lucide-react";
import { Suspense } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { NewMatchAction } from "@/components/league/new-match-action";
import { StandingsContent } from "@/components/league/standings-content";
import { StandingsLoading } from "@/components/league/standings-loading";
import { PageHeader } from "@/components/shared/page-header";

export default function StandingsPage() {
  return (
    <AppShell>
      <PageHeader
        icon={ListOrdered}
        title="Classificação"
        description="Todos os clubes, com 3 pontos por vitória e 1 por empate."
        actions={
          <Suspense fallback={null}>
            <NewMatchAction />
          </Suspense>
        }
      />
      <Suspense fallback={<StandingsLoading />}>
        <StandingsContent />
      </Suspense>
    </AppShell>
  );
}

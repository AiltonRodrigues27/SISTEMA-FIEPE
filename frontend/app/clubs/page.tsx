import { Shield } from "lucide-react";
import { Suspense } from "react";
import { ClubsContent } from "@/components/clubs/clubs-content";
import { ClubsLoading } from "@/components/clubs/clubs-loading";
import { NewClubButton } from "@/components/clubs/new-club-button";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/shared/page-header";
import type { RawSearchParams } from "@/types/search-params.types";

type ClubsPageProps = {
  searchParams: Promise<RawSearchParams>;
};

export default function ClubsPage({ searchParams }: ClubsPageProps) {
  return (
    <AppShell>
      <PageHeader
        icon={Shield}
        title="Clubes"
        description="Cada clube começa com 300,00 em caixa e sem jogadores. A liga aceita no máximo 20 clubes."
        actions={<NewClubButton />}
      />
      <Suspense fallback={<ClubsLoading />}>
        <ClubsContent searchParams={searchParams} />
      </Suspense>
    </AppShell>
  );
}

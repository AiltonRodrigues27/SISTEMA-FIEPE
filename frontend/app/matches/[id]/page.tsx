import { Suspense } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { MatchDetailContent } from "@/components/league/match-detail-content";
import { MatchDetailLoading } from "@/components/league/match-detail-loading";

type MatchPageProps = {
  params: Promise<{ id: string }>;
};

export default function MatchPage({ params }: MatchPageProps) {
  return (
    <AppShell>
      <Suspense fallback={<MatchDetailLoading />}>
        <MatchDetailContent params={params} />
      </Suspense>
    </AppShell>
  );
}

import { Suspense } from "react";
import { ClubDetailContent } from "@/components/clubs/club-detail-content";
import { ClubDetailLoading } from "@/components/clubs/club-detail-loading";
import { AppShell } from "@/components/layout/app-shell";
import type { RawSearchParams } from "@/types/search-params.types";

type ClubPageProps = {
  params: Promise<{ id: string }>;
  searchParams: Promise<RawSearchParams>;
};

export default function ClubPage({ params, searchParams }: ClubPageProps) {
  return (
    <AppShell>
      <Suspense fallback={<ClubDetailLoading />}>
        <ClubDetailContent params={params} searchParams={searchParams} />
      </Suspense>
    </AppShell>
  );
}

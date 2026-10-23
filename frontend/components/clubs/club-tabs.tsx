"use client";

import { useRouter } from "next/navigation";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { parseClubTab } from "@/schemas/transactions-filters.schema";
import { buildClubHref, type ClubTab } from "@/utils/club-href";

type ClubTabsProps = {
  clubId: number;
  tab: ClubTab;
  squadCount: number;
  historyCount?: number;
};

export function ClubTabs({
  clubId,
  tab,
  squadCount,
  historyCount,
}: ClubTabsProps) {
  const router = useRouter();

  return (
    <Tabs
      value={tab}
      onValueChange={(value) =>
        router.replace(buildClubHref(clubId, { tab: parseClubTab(String(value)) }))
      }
    >
      <TabsList variant="line">
        <TabsTrigger value="squad">
          Elenco
          <span className="text-muted-foreground">{squadCount}</span>
        </TabsTrigger>
        <TabsTrigger value="lineup">Escalação</TabsTrigger>
        <TabsTrigger value="history">
          Histórico
          {historyCount !== undefined && (
            <span className="text-muted-foreground">{historyCount}</span>
          )}
        </TabsTrigger>
      </TabsList>
    </Tabs>
  );
}

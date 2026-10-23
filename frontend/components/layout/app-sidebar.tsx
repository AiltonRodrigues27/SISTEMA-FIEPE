import Image from "next/image";
import { Suspense } from "react";
import { SidebarData } from "@/components/layout/sidebar-data";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
} from "@/components/ui/sidebar";

function SidebarFallback() {
  return (
    <SidebarContent>
      <div role="status" className="flex flex-col gap-2 p-2">
        <span className="sr-only">Carregando o menu…</span>
        {Array.from({ length: 6 }, (_, index) => (
          <Skeleton key={index} className="h-8 w-full" />
        ))}
      </div>
    </SidebarContent>
  );
}

export function AppSidebar() {
  return (
    <Sidebar variant="inset">
      <SidebarHeader className="flex-row items-center gap-3 px-4 py-3">
        <Image src="/brand/passe-mark.svg" alt="" width={32} height={32} />
        <div className="flex flex-col">
          <span className="text-body-sm font-semibold">Passe</span>
          <span className="text-caption text-muted-foreground">
            Gestão da liga
          </span>
        </div>
      </SidebarHeader>
      <Suspense fallback={<SidebarFallback />}>
        <SidebarData />
      </Suspense>
    </Sidebar>
  );
}

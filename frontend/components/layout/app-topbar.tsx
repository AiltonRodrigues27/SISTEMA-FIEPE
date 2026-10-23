"use client";

import { ChevronRight, RefreshCw } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useTransition } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import { navigationGroups } from "@/utils/navigation";

function findBreadcrumb(pathname: string): string[] {
  const section = `/${pathname.split("/")[1]}`;

  for (const group of navigationGroups) {
    const item = group.items.find(({ href }) => href === section);
    if (item) return [group.label, item.label];
  }

  return [];
}

export function AppTopbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const breadcrumb = findBreadcrumb(pathname);

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger aria-label="Recolher o menu" />
      <Separator orientation="vertical" className="mx-1 data-vertical:h-4" />
      <nav aria-label="Você está em" className="flex-1">
        <ol className="flex items-center gap-2 text-body-sm">
          {breadcrumb.map((label, index) => (
            <li key={label} className="flex items-center gap-2">
              {index > 0 && (
                <ChevronRight
                  className="size-4 text-muted-foreground"
                  aria-hidden
                />
              )}
              <span
                aria-current={
                  index === breadcrumb.length - 1 ? "page" : undefined
                }
                className={cn(
                  index < breadcrumb.length - 1 && "text-muted-foreground",
                )}
              >
                {label}
              </span>
            </li>
          ))}
        </ol>
      </nav>
      <Button
        variant="ghost"
        size="icon-sm"
        aria-label="Atualizar dados"
        onClick={() => startTransition(() => router.refresh())}
      >
        <RefreshCw className={cn(isPending && "animate-spin")} />
      </Button>
    </header>
  );
}

import { ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import type { PageMeta } from "@/types/players.types";
import type { RawSearchParams } from "@/types/search-params.types";
import { pluralize } from "@/utils/format";

type PlayersPaginationProps = {
  meta: PageMeta;
  searchParams: RawSearchParams;
};

function buildHref(searchParams: RawSearchParams, page: number): string {
  const params = new URLSearchParams();

  for (const [key, value] of Object.entries(searchParams)) {
    const text = Array.isArray(value) ? value[0] : value;
    if (key !== "page" && text) params.set(key, text);
  }
  if (page > 1) params.set("page", String(page));

  const query = params.toString();
  return query ? `/players?${query}` : "/players";
}

function getFirstLastAndNearbyPages(
  current: number,
  total: number,
): (number | "gap")[] {
  const pages = new Set(
    [1, total, current - 1, current, current + 1].filter(
      (page) => page >= 1 && page <= total,
    ),
  );
  const sorted = [...pages].sort((a, b) => a - b);

  return sorted.flatMap((page, index) =>
    index > 0 && page - sorted[index - 1] > 1 ? ["gap" as const, page] : [page],
  );
}

export function PlayersPagination({
  meta,
  searchParams,
}: PlayersPaginationProps) {
  const first = (meta.page - 1) * meta.limit + 1;
  const last = Math.min(meta.page * meta.limit, meta.total_items);

  return (
    <div className="flex flex-col gap-3 border-t px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-body-sm text-muted-foreground">
        Mostrando {first}–{last} de {meta.total_items}{" "}
        {pluralize(meta.total_items, "jogador", "jogadores")}
      </p>
      {meta.total_pages > 1 && (
        <nav aria-label="Páginas" className="flex items-center gap-1">
          {meta.page > 1 ? (
            <Button
              variant="ghost"
              size="sm"
              nativeButton={false}
              render={<Link href={buildHref(searchParams, meta.page - 1)} />}
            >
              <ChevronLeft />
              Anterior
            </Button>
          ) : (
            <Button variant="ghost" size="sm" disabled>
              <ChevronLeft />
              Anterior
            </Button>
          )}
          {getFirstLastAndNearbyPages(meta.page, meta.total_pages).map(
            (page, index) =>
              page === "gap" ? (
                <span
                  key={`gap-${index}`}
                  aria-hidden
                  className="px-1 text-muted-foreground"
                >
                  …
                </span>
              ) : (
                <Button
                  key={page}
                  variant={page === meta.page ? "outline" : "ghost"}
                  size="icon-sm"
                  nativeButton={false}
                  aria-current={page === meta.page ? "page" : undefined}
                  aria-label={`Página ${page}`}
                  render={<Link href={buildHref(searchParams, page)} />}
                >
                  {page}
                </Button>
              ),
          )}
          {meta.page < meta.total_pages ? (
            <Button
              variant="ghost"
              size="sm"
              nativeButton={false}
              render={<Link href={buildHref(searchParams, meta.page + 1)} />}
            >
              Próxima
              <ChevronRight />
            </Button>
          ) : (
            <Button variant="ghost" size="sm" disabled>
              Próxima
              <ChevronRight />
            </Button>
          )}
        </nav>
      )}
    </div>
  );
}

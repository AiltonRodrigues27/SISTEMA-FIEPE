import { ListLoading } from "@/components/shared/list-loading";
import { Skeleton } from "@/components/ui/skeleton";

const COLUMNS = ["Data e hora", "Mandante", "Placar", "Visitante", "Resultado"];

export function MatchesLoading() {
  return (
    <ListLoading
      label="Carregando partidas…"
      columns={COLUMNS}
      rows={5}
      toolbar={<Skeleton className="h-9 w-56" />}
    />
  );
}

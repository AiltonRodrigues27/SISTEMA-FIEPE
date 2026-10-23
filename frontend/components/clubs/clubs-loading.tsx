import { ListLoading } from "@/components/shared/list-loading";
import { Skeleton } from "@/components/ui/skeleton";

const COLUMNS = ["Clube", "Sigla", "Caixa", "Valor do elenco", "Patrimônio"];

export function ClubsLoading() {
  return (
    <ListLoading
      label="Carregando clubes…"
      columns={COLUMNS}
      rows={6}
      toolbar={<Skeleton className="h-9 w-56" />}
    />
  );
}

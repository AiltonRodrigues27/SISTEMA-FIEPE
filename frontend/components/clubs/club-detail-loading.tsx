import { ListLoading } from "@/components/shared/list-loading";
import { Skeleton } from "@/components/ui/skeleton";

const COLUMNS = [
  "Jogador",
  "Posição",
  "Overall",
  "Condição",
  "Valor de mercado",
  "Valor de compra",
  "Fim da fidelidade",
  "Dias restantes",
  "% de multa",
];

export function ClubDetailLoading() {
  return (
    <>
      <div className="flex items-center gap-4">
        <Skeleton className="size-12 rounded-xl" />
        <Skeleton className="h-8 w-56" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <Skeleton key={index} className="h-28 rounded-xl" />
        ))}
      </div>
      <ListLoading label="Carregando o clube…" columns={COLUMNS} rows={6} />
    </>
  );
}

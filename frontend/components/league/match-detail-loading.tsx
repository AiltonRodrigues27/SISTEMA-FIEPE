import { ListLoading } from "@/components/shared/list-loading";
import { Skeleton } from "@/components/ui/skeleton";

const COLUMNS = [
  "Duelo",
  "Atacante",
  "Ataque",
  "Defensor",
  "Defesa",
  "Resultado",
];

export function MatchDetailLoading() {
  return (
    <>
      <Skeleton className="h-28 rounded-xl" />
      <ListLoading
        label="Carregando a partida…"
        columns={COLUMNS}
        rows={6}
      />
    </>
  );
}

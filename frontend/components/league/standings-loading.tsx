import { ListLoading } from "@/components/shared/list-loading";

const COLUMNS = ["#", "Clube", "J", "V", "E", "D", "GP", "GC", "SG", "Pts"];

export function StandingsLoading() {
  return (
    <ListLoading
      label="Carregando a classificação…"
      columns={COLUMNS}
      rows={6}
    />
  );
}

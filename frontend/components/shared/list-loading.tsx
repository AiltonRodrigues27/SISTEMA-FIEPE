import type { ReactNode } from "react";
import { ListCard } from "@/components/shared/list-card";
import { LoadingLabel } from "@/components/shared/loading-label";
import { TableSkeleton } from "@/components/shared/table-skeleton";

type ListLoadingProps = {
  label: string;
  columns: string[];
  rows?: number;
  toolbar?: ReactNode;
};

export function ListLoading({
  label,
  columns,
  rows,
  toolbar,
}: ListLoadingProps) {
  return (
    <ListCard>
      <div className="flex items-center justify-between gap-3 p-4">
        <LoadingLabel>{label}</LoadingLabel>
        {toolbar}
      </div>
      <TableSkeleton columns={columns} rows={rows} />
    </ListCard>
  );
}

import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const BAR_WIDTHS = ["w-3/4", "w-1/2", "w-2/3", "w-1/3", "w-3/5"];

type TableSkeletonProps = {
  columns: string[];
  rows?: number;
};

export function TableSkeleton({ columns, rows = 8 }: TableSkeletonProps) {
  const template = {
    gridTemplateColumns: `repeat(${columns.length}, minmax(0, 1fr))`,
  };

  return (
    <div aria-hidden className="overflow-x-auto">
      <div className="min-w-176">
        <div
          className="grid h-10 items-center gap-4 border-y bg-muted-subtle px-4 text-body-sm text-muted-foreground"
          style={template}
        >
          {columns.map((column) => (
            <span key={column}>{column}</span>
          ))}
        </div>
        {Array.from({ length: rows }, (_, row) => (
          <div
            key={row}
            className="grid h-14 items-center gap-4 border-b px-4 last:border-b-0"
            style={template}
          >
            {columns.map((column, index) => (
              <div key={column} className="flex items-center gap-3">
                {index === 0 && (
                  <Skeleton className="size-8 shrink-0 rounded-full" />
                )}
                <Skeleton
                  className={cn(
                    "h-4",
                    BAR_WIDTHS[(index + row) % BAR_WIDTHS.length],
                  )}
                />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

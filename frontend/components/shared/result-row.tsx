import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type ResultRowProps = {
  title: string;
  caption?: string;
  value: ReactNode;
  variant?: "default" | "total" | "strong";
};

export function ResultRow({
  title,
  caption,
  value,
  variant = "default",
}: ResultRowProps) {
  const isBold = variant !== "default";

  return (
    <div
      className={cn(
        "flex items-center justify-between gap-4 px-3 py-2.5",
        variant === "total" && "bg-muted-subtle",
      )}
    >
      <div className="flex flex-col">
        <dt
          className={cn(
            "text-body-sm",
            isBold && "font-semibold",
            !isBold && !caption && "text-muted-foreground",
          )}
        >
          {title}
        </dt>
        {caption && (
          <span className="text-caption text-muted-foreground">{caption}</span>
        )}
      </div>
      <dd
        className={cn(
          "text-body-sm tabular-nums",
          isBold ? "font-semibold" : "font-medium",
        )}
      >
        {value}
      </dd>
    </div>
  );
}

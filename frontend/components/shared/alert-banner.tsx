import { CircleAlert, TriangleAlert } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const STYLES = {
  warning:
    "border-warning-soft-border bg-warning-soft text-warning-soft-foreground",
  danger:
    "border-destructive-soft-border bg-destructive-soft text-destructive-soft-foreground",
};

type AlertBannerProps = {
  variant: keyof typeof STYLES;
  title: string;
  children?: ReactNode;
};

export function AlertBanner({ variant, title, children }: AlertBannerProps) {
  const Icon = variant === "danger" ? CircleAlert : TriangleAlert;

  return (
    <div
      role={variant === "danger" ? "alert" : "status"}
      className={cn(
        "flex items-start gap-2 rounded-lg border p-3",
        STYLES[variant],
      )}
    >
      <Icon className="mt-0.5 size-4 shrink-0" aria-hidden />
      <div className="flex flex-col gap-0.5">
        <p className="text-body-sm font-medium">{title}</p>
        {children && <p className="text-body-sm">{children}</p>}
      </div>
    </div>
  );
}

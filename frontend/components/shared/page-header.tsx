import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

type PageHeaderProps = {
  icon: LucideIcon;
  title: string;
  description: ReactNode;
  actions?: ReactNode;
};

export function PageHeader({
  icon: Icon,
  title,
  description,
  actions,
}: PageHeaderProps) {
  return (
    <header className="flex flex-col gap-4 sm:flex-row sm:items-center">
      <div className="flex min-w-0 flex-1 items-center gap-4">
        <span className="flex size-12 shrink-0 items-center justify-center rounded-xl border border-primary bg-primary-soft text-primary">
          <Icon className="size-5" aria-hidden />
        </span>
        <div className="flex min-w-0 flex-col gap-1">
          <h1 className="text-heading-page-mobile md:text-heading-page">
            {title}
          </h1>
          <div className="text-body-sm text-muted-foreground">
            {description}
          </div>
        </div>
      </div>
      {actions}
    </header>
  );
}

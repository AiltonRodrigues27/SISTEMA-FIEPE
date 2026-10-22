import { ChevronRight, type LucideIcon } from "lucide-react";

type StepCardProps = {
  number: string;
  icon: LucideIcon;
  title: string;
  description: string;
  hasNext: boolean;
};

export function StepCard({
  number,
  icon: Icon,
  title,
  description,
  hasNext,
}: StepCardProps) {
  return (
    <li className="flex items-center gap-2">
      <div className="flex w-full flex-col gap-2.5 rounded-xl border bg-card p-3.5 shadow-xs xl:h-[158px] xl:w-[172px]">
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary-soft text-primary">
            <Icon className="size-4" aria-hidden />
          </span>
          <span className="font-mono text-caption text-muted-foreground">
            {number}
          </span>
        </div>
        <div className="flex flex-col gap-0.5">
          <h2 className="text-body-sm font-medium">{title}</h2>
          <p className="text-caption text-muted-foreground">{description}</p>
        </div>
      </div>
      {hasNext && (
        <ChevronRight
          className="hidden size-4 shrink-0 text-muted-foreground xl:block"
          aria-hidden
        />
      )}
    </li>
  );
}

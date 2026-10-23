import { cn } from "@/lib/utils";

type ClubTileProps = {
  acronym: string;
  className?: string;
};

export function ClubTile({ acronym, className }: ClubTileProps) {
  return (
    <span
      aria-hidden
      className={cn(
        "flex h-8 min-w-10 shrink-0 items-center justify-center rounded-md border bg-background px-1.5 text-caption font-medium",
        className,
      )}
    >
      {acronym}
    </span>
  );
}

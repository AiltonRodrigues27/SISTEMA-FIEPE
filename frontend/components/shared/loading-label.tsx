import { Loader2 } from "lucide-react";

export function LoadingLabel({ children }: { children: string }) {
  return (
    <p
      role="status"
      className="flex items-center gap-2 text-caption text-muted-foreground"
    >
      <Loader2 className="size-3.5 animate-spin" aria-hidden />
      {children}
    </p>
  );
}

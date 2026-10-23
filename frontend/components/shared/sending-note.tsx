"use client";

import { Info } from "lucide-react";
import type { ReactNode } from "react";
import { useFormStatus } from "react-dom";

export function SendingNote({ children }: { children: ReactNode }) {
  const { pending } = useFormStatus();

  if (!pending) return null;

  return (
    <p
      role="status"
      className="flex items-center gap-2 rounded-lg border bg-muted-subtle p-3 text-caption text-muted-foreground"
    >
      <Info className="size-3.5 shrink-0" aria-hidden />
      {children}
    </p>
  );
}

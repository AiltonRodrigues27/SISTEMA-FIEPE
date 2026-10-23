import type { ReactNode } from "react";

export function ListCard({ children }: { children: ReactNode }) {
  return (
    <section className="overflow-hidden rounded-xl border bg-card shadow-xs">
      {children}
    </section>
  );
}

"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useTransition } from "react";

type FilterChanges = Record<string, string | null>;

export function useFilterPlayer() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();

  function updateFilters(changes: FilterChanges) {
    const params = new URLSearchParams(searchParams.toString());

    for (const [name, value] of Object.entries(changes)) {
      const isEmpty = value === null || value === "";
      if (isEmpty) params.delete(name);
      else params.set(name, value);
    }

    const isChangingPage = "page" in changes;
    if (!isChangingPage) params.delete("page");

    const query = params.toString();
    startTransition(() => {
      router.replace(query ? `${pathname}?${query}` : pathname);
    });
  }

  return { searchParams, updateFilters };
}

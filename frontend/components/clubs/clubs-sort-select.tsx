"use client";

import { ArrowUpDown } from "lucide-react";
import { useRouter } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ClubSort } from "@/types/clubs.types";

const SORT_OPTIONS = [
  { value: "name", label: "Nome" },
  { value: "net_worth_desc", label: "Patrimônio (maior para o menor)" },
  { value: "net_worth_asc", label: "Patrimônio (menor para o maior)" },
];

export function ClubsSortSelect({ sort }: { sort: ClubSort }) {
  const router = useRouter();

  return (
    <Select
      items={SORT_OPTIONS}
      value={sort}
      onValueChange={(value) =>
        router.replace(value === "name" ? "/clubs" : `/clubs?sort=${value}`)
      }
    >
      <SelectTrigger aria-label="Ordenar clubes" className="h-9 w-full sm:w-80">
        <ArrowUpDown className="text-muted-foreground" aria-hidden />
        <span>Ordenar:</span>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Ordenar por</SelectLabel>
          {SORT_OPTIONS.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}

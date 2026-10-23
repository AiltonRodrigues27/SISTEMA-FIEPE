"use client";

import { ArrowUpDown } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useFilterPlayer } from "@/hooks/use-filter-player";

const SORT_OPTIONS = [
  { value: "name", label: "Nome" },
  { value: "value_desc", label: "Maior valor de mercado" },
  { value: "value_asc", label: "Menor valor de mercado" },
  { value: "age_desc", label: "Maior idade" },
  { value: "age_asc", label: "Menor idade" },
  { value: "position", label: "Posição (GOL a ATA)" },
];

type PlayersToolbarProps = {
  counts: { all: number; free: number; club: number } | null;
};

export function PlayersToolbar({ counts }: PlayersToolbarProps) {
  const { searchParams, updateFilters } = useFilterPlayer();

  const freeParam = searchParams.get("free");
  const tab =
    freeParam === "true" ? "free" : freeParam === "false" ? "club" : "all";
  const sort = searchParams.get("sort") ?? "name";
  // A API recusa "livres" junto com clube, então a aba fica indisponível.
  const hasClubFilter = searchParams.has("club_id");

  function changeTab(value: string) {
    if (value === "free") updateFilters({ free: "true", club_id: null });
    else if (value === "club") updateFilters({ free: "false" });
    else updateFilters({ free: null });
  }

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-4">
      <Tabs value={tab} onValueChange={(value) => changeTab(String(value))}>
        <TabsList>
          <TabsTrigger value="all">
            Todos
            {counts && (
              <span className="text-muted-foreground">{counts.all}</span>
            )}
          </TabsTrigger>
          <TabsTrigger value="free" disabled={hasClubFilter}>
            Livres
            {counts && !hasClubFilter && (
              <span className="text-muted-foreground">{counts.free}</span>
            )}
          </TabsTrigger>
          <TabsTrigger value="club">
            Em clubes
            {counts && (
              <span className="text-muted-foreground">{counts.club}</span>
            )}
          </TabsTrigger>
        </TabsList>
      </Tabs>
      <Select
        items={SORT_OPTIONS}
        value={sort}
        onValueChange={(value) =>
          updateFilters({ sort: value === "name" ? null : value })
        }
      >
        <SelectTrigger
          aria-label="Ordenar jogadores"
          className="h-9 w-full sm:w-72"
        >
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
    </div>
  );
}

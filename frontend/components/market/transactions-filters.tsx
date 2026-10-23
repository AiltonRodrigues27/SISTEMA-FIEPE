"use client";

import { User } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { TransactionsQuery, TransactionType } from "@/types/market.types";
import { buildClubHref } from "@/utils/club-href";

const ALL_PLAYERS = "all";

const TYPE_OPTIONS: { value: TransactionType; label: string }[] = [
  { value: "COMPRA", label: "Compra" },
  { value: "VENDA", label: "Venda" },
];

type TransactionsFiltersProps = {
  clubId: number;
  filters: TransactionsQuery;
  players: { id: number; name: string }[];
};

export function TransactionsFilters({
  clubId,
  filters,
  players,
}: TransactionsFiltersProps) {
  const router = useRouter();
  const selectedTypes = filters.type
    ? [filters.type]
    : TYPE_OPTIONS.map((option) => option.value);
  const hasFilters =
    filters.type !== undefined || filters.player_id !== undefined;
  const playerItems = [
    { value: ALL_PLAYERS, label: "Todos" },
    ...players.map((player) => ({
      value: String(player.id),
      label: player.name,
    })),
  ];

  function applyFilters(next: TransactionsQuery) {
    router.replace(buildClubHref(clubId, { tab: "history", ...next }));
  }

  function toggleType(type: TransactionType, isChecked: boolean) {
    const types = isChecked
      ? [...selectedTypes, type]
      : selectedTypes.filter((selected) => selected !== type);

    applyFilters({
      ...filters,
      type: types.length === 1 ? types[0] : undefined,
    });
  }

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-3">
      <fieldset className="flex items-center gap-2">
        <legend className="sr-only">Tipo de transação</legend>
        <span aria-hidden className="text-caption text-muted-foreground">
          Tipo:
        </span>
        {TYPE_OPTIONS.map((option) => (
          <Label
            key={option.value}
            htmlFor={`type-${option.value}`}
            className="h-8 cursor-pointer rounded-md border bg-background px-2.5 font-medium has-data-checked:border-primary has-data-checked:bg-primary-soft has-data-checked:text-primary-soft-foreground has-focus-visible:ring-3 has-focus-visible:ring-ring/50"
          >
            <Checkbox
              id={`type-${option.value}`}
              checked={selectedTypes.includes(option.value)}
              onCheckedChange={(isChecked) =>
                toggleType(option.value, isChecked)
              }
            />
            {option.label}
          </Label>
        ))}
      </fieldset>
      <Select
        items={playerItems}
        value={filters.player_id ? String(filters.player_id) : ALL_PLAYERS}
        onValueChange={(value) =>
          applyFilters({
            ...filters,
            player_id: value === ALL_PLAYERS ? undefined : Number(value),
          })
        }
      >
        <SelectTrigger aria-label="Filtrar por jogador" className="h-9 w-56">
          <User className="text-muted-foreground" aria-hidden />
          <span>Jogador:</span>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {playerItems.map((item) => (
            <SelectItem key={item.value} value={item.value}>
              {item.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {hasFilters && (
        <Button variant="link" size="xs" onClick={() => applyFilters({})}>
          Limpar filtros
        </Button>
      )}
    </div>
  );
}

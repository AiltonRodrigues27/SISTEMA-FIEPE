import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ActiveFilterChip } from "@/types/filters.types";

type ActiveFilterChipsProps = {
  chips: ActiveFilterChip[];
  isOnlySearching: boolean;
  onRemove: (keys: string[]) => void;
  onClearAll: () => void;
};

export function ActiveFilterChips({
  chips,
  isOnlySearching,
  onRemove,
  onClearAll,
}: ActiveFilterChipsProps) {
  if (chips.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-caption text-muted-foreground">
        {isOnlySearching ? "Resultados para a busca:" : "Filtros ativos:"}
      </span>
      {chips.map((chip) => (
        <button
          key={chip.label}
          type="button"
          onClick={() => onRemove(chip.keys)}
          className="inline-flex h-6 items-center gap-1 rounded-md border bg-background px-2 text-caption font-medium hover:bg-muted"
          aria-label={`Remover filtro ${chip.label}`}
        >
          {chip.label}
          <X className="size-3" aria-hidden />
        </button>
      ))}
      <Button variant="link" size="xs" onClick={onClearAll}>
        Limpar filtros
      </Button>
    </div>
  );
}

"use client";

import { Coins, HeartPulse, Shield, Shirt, User } from "lucide-react";
import { ActiveFilterChips } from "@/components/players/active-filter-chips";
import { FilterSelect } from "@/components/players/filter-select";
import { PlayersSearchField } from "@/components/players/players-search-field";
import { RangeFilter } from "@/components/players/range-filter";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useFilterPlayer } from "@/hooks/use-filter-player";
import type { ClubOption } from "@/types/clubs.types";
import type { ActiveFilterChip } from "@/types/filters.types";
import { formatMoney, formatRange } from "@/utils/format";
import {
  CONDITION_LABELS,
  POSITION_LABELS,
  findLabel,
} from "@/utils/labels";

export function PlayersFilters({ clubs }: { clubs: ClubOption[] }) {
  const { searchParams, updateFilters } = useFilterPlayer();

  const search = searchParams.get("search") ?? "";
  const position = searchParams.get("position");
  const condition = searchParams.get("condition");
  const clubId = searchParams.get("club_id");
  const minAge = searchParams.get("min_age") ?? "";
  const maxAge = searchParams.get("max_age") ?? "";
  const minValue = searchParams.get("min_value") ?? "";
  const maxValue = searchParams.get("max_value") ?? "";
  const isFreeOnly = searchParams.get("free") === "true";

  const chips: ActiveFilterChip[] = [];
  if (search) chips.push({ label: `Busca: ${search}`, keys: ["search"] });
  if (position) {
    const text = findLabel(POSITION_LABELS, position);
    chips.push({ label: `Posição: ${text ?? position}`, keys: ["position"] });
  }
  if (condition) {
    const text = findLabel(CONDITION_LABELS, condition);
    chips.push({
      label: `Condição: ${text ?? condition}`,
      keys: ["condition"],
    });
  }
  if (clubId) {
    const club = clubs.find(({ id }) => String(id) === clubId);
    chips.push({
      label: `Clube: ${club?.name ?? clubId}`,
      keys: ["club_id"],
    });
  }
  if (minAge || maxAge) {
    chips.push({
      label: `Idade: ${formatRange(minAge, maxAge, String)}`,
      keys: ["min_age", "max_age"],
    });
  }
  if (minValue || maxValue) {
    chips.push({
      label: `Valor de mercado: ${formatRange(minValue, maxValue, formatMoney)}`,
      keys: ["min_value", "max_value"],
    });
  }

  const isOnlySearching = chips.length === 1 && search !== "";

  function clearAll() {
    updateFilters({
      search: null,
      position: null,
      condition: null,
      club_id: null,
      min_age: null,
      max_age: null,
      min_value: null,
      max_value: null,
    });
  }

  const clubSelect = (
    <FilterSelect
      icon={Shield}
      placeholder="Clube"
      allLabel="Todos os clubes"
      value={isFreeOnly ? null : clubId}
      disabled={isFreeOnly}
      options={clubs.map((club) => ({
        value: String(club.id),
        label: club.name,
      }))}
      onChange={(value) => updateFilters({ club_id: value })}
    />
  );

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <PlayersSearchField
          urlValue={search}
          onSearch={(value) => updateFilters({ search: value || null })}
        />
        <FilterSelect
          icon={Shirt}
          placeholder="Posição"
          allLabel="Todas as posições"
          value={position}
          options={Object.entries(POSITION_LABELS).map(([value, label]) => ({
            value,
            label,
          }))}
          onChange={(value) => updateFilters({ position: value })}
        />
        <FilterSelect
          icon={HeartPulse}
          placeholder="Condição"
          allLabel="Todas as condições"
          value={condition}
          options={Object.entries(CONDITION_LABELS).map(([value, label]) => ({
            value,
            label,
          }))}
          onChange={(value) => updateFilters({ condition: value })}
        />
        {isFreeOnly ? (
          <Tooltip>
            <TooltipTrigger render={<span className="inline-flex" />}>
              {clubSelect}
            </TooltipTrigger>
            <TooltipContent>
              “Livres” não combina com o filtro por clube.
            </TooltipContent>
          </Tooltip>
        ) : (
          clubSelect
        )}
        <RangeFilter
          key={`age-${minAge}-${maxAge}`}
          icon={User}
          label="Idade"
          activeLabel="Idade"
          activeText={
            minAge || maxAge ? formatRange(minAge, maxAge, String) : null
          }
          limits={{ min: 16, max: 45, integer: true }}
          minKey="min_age"
          maxKey="max_age"
          minValue={minAge}
          maxValue={maxAge}
          onApply={updateFilters}
        />
        <RangeFilter
          key={`value-${minValue}-${maxValue}`}
          icon={Coins}
          label="Valor de mercado"
          activeLabel="Valor"
          activeText={
            minValue || maxValue
              ? formatRange(minValue, maxValue, formatMoney)
              : null
          }
          limits={{ min: 0, max: 550, integer: false }}
          minKey="min_value"
          maxKey="max_value"
          minValue={minValue}
          maxValue={maxValue}
          onApply={updateFilters}
        />
      </div>
      <ActiveFilterChips
        chips={chips}
        isOnlySearching={isOnlySearching}
        onRemove={(keys) =>
          updateFilters(Object.fromEntries(keys.map((key) => [key, null])))
        }
        onClearAll={clearAll}
      />
    </div>
  );
}

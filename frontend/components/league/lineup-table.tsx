import { ConditionBadge } from "@/components/players/condition-badge";
import {
  TABLE_CELL_CLASS as CELL,
  TABLE_HEAD_CLASS as HEAD,
} from "@/components/shared/table-classes";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { LineupRow } from "@/types/league.types";
import type { Player } from "@/types/players.types";

function describeNoOptions(positions: Player["position"][]): string {
  return positions.length > 1
    ? `Sem ${positions.join(" ou ")}`
    : `Sem ${positions[0]} no elenco`;
}

type LineupTableProps = {
  rows: LineupRow[];
  onChange: (slotKey: string, playerId: string | null) => void;
};

export function LineupTable({ rows, onChange }: LineupTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
          <TableHead className={HEAD}>Vaga</TableHead>
          <TableHead className={cn(HEAD, "min-w-56")}>Titular</TableHead>
          <TableHead className={HEAD}>Condição</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Overall</TableHead>
          <TableHead className={cn(HEAD, "min-w-40")}>
            Atributos usados
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map(({ slot, selectedId, player, options, attributes }) => {
          const positions = slot.positions.join(" ou ");

          return (
            <TableRow key={slot.key} className="h-16">
              <TableCell className={CELL}>
                <div className="flex flex-col">
                  <span className="text-body-sm font-medium">{slot.label}</span>
                  <span className="text-caption text-muted-foreground">
                    {positions}
                  </span>
                </div>
              </TableCell>
              <TableCell className={CELL}>
                <Select
                  name="player_ids"
                  items={options}
                  value={selectedId}
                  onValueChange={(value) => onChange(slot.key, value)}
                  disabled={options.length === 0}
                >
                  <SelectTrigger
                    aria-label={`Titular da vaga ${slot.label} (${positions})`}
                    className="h-9 w-full min-w-52"
                  >
                    <SelectValue
                      placeholder={
                        options.length === 0
                          ? describeNoOptions(slot.positions)
                          : "Escolha o titular"
                      }
                    />
                  </SelectTrigger>
                  <SelectContent>
                    {options.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </TableCell>
              <TableCell className={CELL}>
                {player ? <ConditionBadge condition={player.condition} /> : "—"}
              </TableCell>
              <TableCell
                className={cn(CELL, "text-right text-body-sm font-semibold")}
              >
                {player?.overall ?? "—"}
              </TableCell>
              <TableCell className={CELL}>
                {attributes.length === 0 ? (
                  "—"
                ) : (
                  <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-body-sm">
                    {attributes.map((attribute) => (
                      <span key={attribute.label}>
                        <span className="text-muted-foreground">
                          {attribute.label}
                        </span>{" "}
                        <span className="font-medium">{attribute.value}</span>
                      </span>
                    ))}
                  </div>
                )}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

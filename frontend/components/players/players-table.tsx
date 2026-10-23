import Link from "next/link";
import { ConditionBadge } from "@/components/players/condition-badge";
import { PlayerAvatar } from "@/components/players/player-avatar";
import { BuyPlayerButton } from "@/components/market/buy-player-button";
import { PlayerRowActions } from "@/components/players/player-row-actions";
import {
  TABLE_CELL_CLASS as CELL,
  TABLE_HEAD_CLASS as HEAD,
} from "@/components/shared/table-classes";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { Club } from "@/types/clubs.types";
import type { Player } from "@/types/players.types";
import { formatMoney } from "@/utils/format";
import { POSITION_LABELS } from "@/utils/labels";

function AgilityBar({ value }: { value: number }) {
  const tone =
    value >= 80
      ? "bg-success"
      : value < 40
        ? "bg-destructive"
        : "bg-muted-foreground";

  return (
    <div className="flex items-center justify-end gap-2">
      <span className="text-body-sm tabular-nums">{value}</span>
      <span
        aria-hidden
        className="relative h-1.5 w-10 shrink-0 rounded-[3px] bg-muted"
      >
        <span
          className={cn("absolute inset-y-0 left-0 rounded-[3px]", tone)}
          style={{ width: `${value}%` }}
        />
      </span>
    </div>
  );
}

type PlayersTableProps = {
  players: Player[];
  clubs: Club[];
  starterIds: number[];
};

export function PlayersTable({
  players,
  clubs,
  starterIds,
}: PlayersTableProps) {
  const clubsById = new Map(clubs.map((club) => [club.id, club]));

  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
          <TableHead className={cn(HEAD, "min-w-48")}>Jogador</TableHead>
          <TableHead className={HEAD}>Posição</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Overall</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Agilidade</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Idade</TableHead>
          <TableHead className={HEAD}>Condição</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Valor base</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>
            Valor de mercado
          </TableHead>
          <TableHead className={HEAD}>Clube</TableHead>
          <TableHead className={HEAD}>
            <span className="sr-only">Ações</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {players.map((player) => {
          const club =
            player.club_id === null ? undefined : clubsById.get(player.club_id);

          return (
            <TableRow key={player.id} className="h-14">
              <TableCell className={CELL}>
                <div className="flex items-center gap-3">
                  <PlayerAvatar id={player.id} name={player.name} />
                  <div className="flex min-w-0 flex-col">
                    <span className="text-body-sm font-medium">
                      {player.name}
                    </span>
                    <span className="text-caption text-muted-foreground">
                      {POSITION_LABELS[player.position]}
                    </span>
                  </div>
                </div>
              </TableCell>
              <TableCell className={CELL}>
                <Badge variant="outline">{player.position}</Badge>
              </TableCell>
              <TableCell
                className={cn(CELL, "text-right text-body-sm font-semibold")}
              >
                {player.overall}
              </TableCell>
              <TableCell className={CELL}>
                <AgilityBar value={player.agility} />
              </TableCell>
              <TableCell className={cn(CELL, "text-right text-body-sm")}>
                {player.age}
              </TableCell>
              <TableCell className={CELL}>
                <ConditionBadge condition={player.condition} />
              </TableCell>
              <TableCell
                className={cn(
                  CELL,
                  "text-right text-body-sm text-muted-foreground",
                )}
              >
                {formatMoney(player.base_value)}
              </TableCell>
              <TableCell
                className={cn(CELL, "text-right text-body-sm font-medium")}
              >
                {formatMoney(player.market_value)}
              </TableCell>
              <TableCell className={CELL}>
                {player.club_id === null ? (
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">Livre</Badge>
                    <BuyPlayerButton player={player} clubs={clubs} />
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <span className="text-caption font-medium">
                      {club?.acronym ?? "—"}
                    </span>
                    <Link
                      href={`/clubs/${player.club_id}`}
                      className="text-body-sm underline underline-offset-2"
                    >
                      {club?.name ?? `Clube ${player.club_id}`}
                    </Link>
                  </div>
                )}
              </TableCell>
              <TableCell className={cn(CELL, "text-right")}>
                <PlayerRowActions
                  player={player}
                  clubs={clubs}
                  isStarter={starterIds.includes(player.id)}
                />
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

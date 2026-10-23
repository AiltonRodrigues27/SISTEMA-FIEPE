import { PenaltyBadge } from "@/components/market/penalty-badge";
import { SellPlayerButton } from "@/components/market/sell-player-button";
import { ConditionBadge } from "@/components/players/condition-badge";
import { PlayerAvatar } from "@/components/players/player-avatar";
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
import type { SquadMember } from "@/types/clubs.types";
import { formatDate, formatMoney, formatTime } from "@/utils/format";

type SquadTableProps = {
  squad: SquadMember[];
  clubName: string;
  starterIds: number[];
};

export function SquadTable({ squad, clubName, starterIds }: SquadTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
          <TableHead className={cn(HEAD, "min-w-48")}>Jogador</TableHead>
          <TableHead className={HEAD}>Posição</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Overall</TableHead>
          <TableHead className={HEAD}>Condição</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>
            Valor de mercado
          </TableHead>
          <TableHead className={cn(HEAD, "text-right")}>
            Valor de compra
          </TableHead>
          <TableHead className={HEAD}>Fim da fidelidade</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>
            Dias restantes
          </TableHead>
          <TableHead className={cn(HEAD, "text-right")}>% de multa</TableHead>
          <TableHead className={HEAD}>
            <span className="sr-only">Ações</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {squad.map((member) => (
          <TableRow key={member.id} className="h-14">
            <TableCell className={CELL}>
              <div className="flex items-center gap-3">
                <PlayerAvatar id={member.id} name={member.name} />
                <span className="text-body-sm font-medium">{member.name}</span>
              </div>
            </TableCell>
            <TableCell className={CELL}>
              <Badge variant="outline">{member.position}</Badge>
            </TableCell>
            <TableCell
              className={cn(CELL, "text-right text-body-sm font-semibold")}
            >
              {member.overall}
            </TableCell>
            <TableCell className={CELL}>
              <ConditionBadge condition={member.condition} />
            </TableCell>
            <TableCell
              className={cn(CELL, "text-right text-body-sm font-medium")}
            >
              {formatMoney(member.market_value)}
            </TableCell>
            <TableCell
              className={cn(
                CELL,
                "text-right text-body-sm text-muted-foreground",
              )}
            >
              {member.contract
                ? formatMoney(member.contract.purchase_value)
                : "—"}
            </TableCell>
            <TableCell className={CELL}>
              {member.contract ? (
                <div className="flex flex-col">
                  <span className="text-body-sm">
                    {formatDate(member.contract.loyalty_until)}
                  </span>
                  <span className="text-caption text-muted-foreground">
                    {formatTime(member.contract.loyalty_until)}
                  </span>
                </div>
              ) : (
                "—"
              )}
            </TableCell>
            <TableCell className={cn(CELL, "text-right text-body-sm")}>
              {member.contract?.remaining_days ?? "—"}
            </TableCell>
            <TableCell className={cn(CELL, "text-right")}>
              {member.contract ? (
                <PenaltyBadge rate={member.contract.penalty_rate} />
              ) : (
                "—"
              )}
            </TableCell>
            <TableCell className={cn(CELL, "text-right")}>
              <SellPlayerButton
                member={member}
                clubName={clubName}
                isStarter={starterIds.includes(member.id)}
              />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

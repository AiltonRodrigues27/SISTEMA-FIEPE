import { HandCoins, ShoppingCart } from "lucide-react";
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
import type { Transaction } from "@/types/market.types";
import {
  formatDate,
  formatMoney,
  formatSignedMoney,
  formatTime,
} from "@/utils/format";

function signedTone(value: number): string {
  if (value > 0) return "text-success";
  if (value < 0) return "text-destructive";
  return "";
}

export function TransactionsTable({
  transactions,
}: {
  transactions: Transaction[];
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
          <TableHead className={HEAD}>Data e hora</TableHead>
          <TableHead className={HEAD}>Tipo</TableHead>
          <TableHead className={cn(HEAD, "min-w-44")}>Jogador</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Valor</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>
            Taxa ou comissão
          </TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Multa</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Lucro</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>
            Variação do caixa
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {transactions.map((transaction) => {
          const isPurchase = transaction.type === "COMPRA";
          const TypeIcon = isPurchase ? ShoppingCart : HandCoins;

          return (
            <TableRow key={transaction.id} className="h-12">
              <TableCell className={cn(CELL, "text-body-sm whitespace-nowrap")}>
                {formatDate(transaction.created_at)}{" "}
                <span className="text-muted-foreground">
                  {formatTime(transaction.created_at)}
                </span>
              </TableCell>
              <TableCell className={CELL}>
                <Badge variant="outline">
                  <TypeIcon aria-hidden />
                  {isPurchase ? "Compra" : "Venda"}
                </Badge>
              </TableCell>
              <TableCell className={CELL}>
                <div className="flex items-center gap-3">
                  <PlayerAvatar
                    id={transaction.player_id}
                    name={transaction.player_name}
                  />
                  <span className="text-body-sm font-medium">
                    {transaction.player_name}
                  </span>
                </div>
              </TableCell>
              <TableCell className={cn(CELL, "text-right text-body-sm")}>
                {formatMoney(transaction.value)}
              </TableCell>
              <TableCell className={cn(CELL, "text-right text-body-sm")}>
                {formatMoney(transaction.fee)}
              </TableCell>
              <TableCell className={cn(CELL, "text-right text-body-sm")}>
                {formatMoney(transaction.penalty)}
              </TableCell>
              <TableCell
                className={cn(
                  CELL,
                  "text-right text-body-sm tabular-nums",
                  transaction.profit === null
                    ? "text-muted-foreground"
                    : signedTone(transaction.profit),
                )}
              >
                {transaction.profit === null
                  ? "–"
                  : formatSignedMoney(transaction.profit)}
              </TableCell>
              <TableCell
                className={cn(
                  CELL,
                  "text-right text-body-sm font-medium tabular-nums",
                  signedTone(transaction.cash_change),
                )}
              >
                {formatSignedMoney(transaction.cash_change)}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

import { Check, History } from "lucide-react";
import Link from "next/link";
import { ResultRow } from "@/components/shared/result-row";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import type { SquadMember } from "@/types/clubs.types";
import type { Sale } from "@/types/market.types";
import { buildClubHref } from "@/utils/club-href";
import { formatMoney, formatSignedMoney } from "@/utils/format";

type SaleResultProps = {
  sale: Sale;
  member: SquadMember;
  clubName: string;
  wasStarter: boolean;
  onClose: () => void;
};

export function SaleResult({
  sale,
  member,
  clubName,
  wasStarter,
  onClose,
}: SaleResultProps) {
  const profit = sale.profit ?? 0;
  const fulfilledLoyalty = sale.contract_status === "ENCERRADO";

  return (
    <>
      <DialogHeader>
        <span className="mb-1 flex size-9 items-center justify-center rounded-full bg-success-soft text-success-soft-foreground">
          <Check className="size-4" aria-hidden />
        </span>
        <DialogTitle>Venda concluída</DialogTitle>
        <DialogDescription>
          {member.name} voltou a ficar livre
          {wasStarter ? " e saiu da escalação" : ""}.
          {fulfilledLoyalty
            ? " A fidelidade já tinha terminado, então não houve multa."
            : ""}
        </DialogDescription>
      </DialogHeader>
      <dl className="divide-y overflow-hidden rounded-lg border">
        <ResultRow
          title="Valor de compra"
          value={formatMoney(sale.purchase_value)}
        />
        <ResultRow
          title="Valor de venda"
          caption="Valor de mercado no momento da venda"
          value={formatMoney(sale.value)}
        />
        <ResultRow title="Dias restantes" value={sale.remaining_days} />
        <ResultRow
          title="Multa"
          caption={
            sale.penalty_rate > 0
              ? `${sale.penalty_rate}% do valor de venda, com teto de 10,00`
              : "Fidelidade cumprida: sem multa"
          }
          value={formatMoney(sale.penalty)}
        />
        <ResultRow
          title="Lucro"
          value={
            <span
              className={cn(
                profit > 0 && "text-success",
                profit < 0 && "text-destructive",
              )}
            >
              {formatSignedMoney(profit)}
            </span>
          }
        />
        <ResultRow
          title="Comissão"
          caption={
            profit > 0
              ? "10% do lucro até 10,00 + 20% do que passar"
              : "Sem lucro: sem comissão"
          }
          value={formatMoney(sale.fee)}
        />
        <ResultRow
          title="Crédito no caixa"
          caption="Valor de venda − multa − comissão"
          value={formatSignedMoney(sale.cash_change)}
          variant="total"
        />
        <ResultRow
          title="Contrato"
          value={
            <Badge variant={fulfilledLoyalty ? "outline" : "warning"}>
              <span aria-hidden className="size-1.5 rounded-full bg-current" />
              {sale.contract_status}
            </Badge>
          }
        />
        <ResultRow
          title={`Novo caixa do ${clubName}`}
          value={formatMoney(sale.club_cash)}
          variant="strong"
        />
      </dl>
      <DialogFooter>
        <Button
          variant="outline"
          nativeButton={false}
          render={
            <Link href={buildClubHref(sale.club_id, { tab: "history" })} />
          }
        >
          <History aria-hidden />
          Ver histórico
        </Button>
        <Button type="button" onClick={onClose}>
          Fechar
        </Button>
      </DialogFooter>
    </>
  );
}

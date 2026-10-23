import { ArrowRight, Check } from "lucide-react";
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
import type { Purchase } from "@/types/market.types";
import { formatDate, formatMoney, formatTime } from "@/utils/format";

type PurchaseResultProps = {
  purchase: Purchase;
  clubName: string;
  onClose: () => void;
};

export function PurchaseResult({
  purchase,
  clubName,
  onClose,
}: PurchaseResultProps) {
  const { loyalty_until: loyaltyUntil, status } = purchase.contract;

  return (
    <>
      <DialogHeader>
        <span className="mb-1 flex size-9 items-center justify-center rounded-full bg-success-soft text-success-soft-foreground">
          <Check className="size-4" aria-hidden />
        </span>
        <DialogTitle>Compra concluída</DialogTitle>
        <DialogDescription>
          {purchase.player_name} agora é do {clubName}.
        </DialogDescription>
      </DialogHeader>
      <dl className="divide-y overflow-hidden rounded-lg border">
        <ResultRow
          title="Valor"
          caption="Valor de mercado no momento da compra"
          value={formatMoney(purchase.value)}
        />
        <ResultRow
          title="Taxa"
          caption={
            purchase.fee > 0
              ? "5% do valor, porque passa de 30,00"
              : "Sem taxa, porque o valor não passa de 30,00"
          }
          value={formatMoney(purchase.fee)}
        />
        <ResultRow
          title="Custo total"
          caption="Valor + taxa"
          value={formatMoney(purchase.value + purchase.fee)}
          variant="total"
        />
        <ResultRow
          title="Fim da fidelidade"
          value={`${formatDate(loyaltyUntil)}, ${formatTime(loyaltyUntil)}`}
        />
        <ResultRow
          title="Contrato"
          value={
            <Badge variant="success">
              <span aria-hidden className="size-1.5 rounded-full bg-current" />
              {status}
            </Badge>
          }
        />
        <ResultRow
          title={`Novo caixa do ${clubName}`}
          value={formatMoney(purchase.club_cash)}
          variant="strong"
        />
      </dl>
      <DialogFooter>
        <Button
          variant="outline"
          nativeButton={false}
          render={<Link href={`/clubs/${purchase.club_id}`} />}
        >
          Ver clube
          <ArrowRight aria-hidden />
        </Button>
        <Button type="button" onClick={onClose}>
          Fechar
        </Button>
      </DialogFooter>
    </>
  );
}

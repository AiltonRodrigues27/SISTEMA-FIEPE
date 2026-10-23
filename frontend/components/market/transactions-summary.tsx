import {
  Gavel,
  HandCoins,
  Percent,
  ShoppingCart,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { TransactionSummary } from "@/types/market.types";
import { formatMoney, formatSignedMoney } from "@/utils/format";

export function TransactionsSummary({
  summary,
}: {
  summary: TransactionSummary;
}) {
  const items = [
    {
      icon: ShoppingCart,
      label: "Total pago em compras",
      value: formatMoney(summary.total_spent),
      hint: "Valor + taxa",
    },
    {
      icon: HandCoins,
      label: "Total recebido em vendas",
      value: formatMoney(summary.total_received),
      hint: "Crédito líquido",
    },
    {
      icon: Percent,
      label: "Taxas e comissões",
      value: formatMoney(summary.total_fees),
      hint: "Somadas",
    },
    {
      icon: Gavel,
      label: "Multas",
      value: formatMoney(summary.total_penalties),
      hint: "Por fidelidade",
    },
    {
      icon: TrendingUp,
      label: "Lucro total",
      value: formatSignedMoney(summary.total_profit),
      hint: "Soma dos lucros, com sinal",
      tone:
        summary.total_profit > 0
          ? "text-success"
          : summary.total_profit < 0
            ? "text-destructive"
            : "",
    },
  ];

  return (
    <dl className="grid gap-4 border-t px-4 py-4 sm:grid-cols-2 lg:grid-cols-5">
      {items.map(({ icon: Icon, label, value, hint, tone }) => (
        <div key={label} className="flex flex-col gap-0.5">
          <dt className="flex items-center gap-1.5 text-caption text-muted-foreground">
            <Icon className="size-3.5 shrink-0" aria-hidden />
            {label}
          </dt>
          <dd className={cn("text-heading-card tabular-nums", tone)}>
            {value}
          </dd>
          <span className="text-caption text-muted-foreground">{hint}</span>
        </div>
      ))}
    </dl>
  );
}

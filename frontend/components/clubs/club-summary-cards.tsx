import { Landmark, Shirt, Tag, Wallet } from "lucide-react";
import type { Club } from "@/types/clubs.types";
import { formatMoney } from "@/utils/format";

type ClubSummaryCardsProps = {
  club: Club;
  squadCount: number;
  squadLimit: number;
};

export function ClubSummaryCards({
  club,
  squadCount,
  squadLimit,
}: ClubSummaryCardsProps) {
  const cards = [
    {
      icon: Wallet,
      label: "Caixa",
      value: formatMoney(club.cash),
      unit: "moedas",
      hint: "Só muda por compras e vendas",
    },
    {
      icon: Tag,
      label: "Valor do elenco",
      value: formatMoney(club.squad_value),
      unit: "moedas",
      hint: "Soma dos valores de mercado",
    },
    {
      icon: Landmark,
      label: "Patrimônio",
      value: formatMoney(club.net_worth),
      unit: "moedas",
      hint: "Caixa + valor do elenco",
    },
    {
      icon: Shirt,
      label: "Elenco",
      value: `${squadCount} de ${squadLimit}`,
      unit: null,
      hint: `Limite de ${squadLimit} jogadores`,
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map(({ icon: Icon, label, value, unit, hint }) => (
        <section
          key={label}
          className="flex flex-col gap-2 rounded-xl border bg-card p-5 shadow-xs"
        >
          <div className="flex items-center justify-between text-body-sm text-muted-foreground">
            {label}
            <Icon className="size-4" aria-hidden />
          </div>
          <p className="flex items-baseline gap-1.5">
            <span className="text-display-kpi tabular-nums">{value}</span>
            {unit && (
              <span className="text-caption text-muted-foreground">{unit}</span>
            )}
          </p>
          <p className="text-caption text-muted-foreground">{hint}</p>
        </section>
      ))}
    </div>
  );
}

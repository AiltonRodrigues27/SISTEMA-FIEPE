import { Lock } from "lucide-react";
import { ConditionBadge } from "@/components/players/condition-badge";
import { PlayerAvatar } from "@/components/players/player-avatar";
import type { Player } from "@/types/players.types";
import { POSITION_LABELS } from "@/utils/labels";

type ReservesCardProps = {
  reserves: Player[];
  squadCount: number;
};

function describeNoReserves(squadCount: number): string {
  if (squadCount === 0) return "Nenhuma reserva: o elenco está vazio.";
  if (squadCount === 1) {
    return "Nenhuma reserva: o jogador do elenco está escolhido.";
  }
  return `Nenhuma reserva: os ${squadCount} jogadores do elenco estão escolhidos.`;
}

export function ReservesCard({ reserves, squadCount }: ReservesCardProps) {
  const hasSickReserve = reserves.some(
    (player) => player.condition === "DOENTE",
  );

  return (
    <section className="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-xs">
      <div className="flex flex-col gap-1">
        <h2 className="text-heading-card">Reservas</h2>
        <p className="text-caption text-muted-foreground">
          Jogadores do elenco fora da escalação.
        </p>
      </div>
      {reserves.length === 0 ? (
        <p className="text-body-sm text-muted-foreground">
          {describeNoReserves(squadCount)}
        </p>
      ) : (
        <ul className="flex flex-col gap-2">
          {reserves.map((player) => (
            <li key={player.id} className="flex items-center gap-2.5">
              <PlayerAvatar id={player.id} name={player.name} />
              <div className="flex min-w-0 flex-1 flex-col">
                <span className="truncate text-body-sm font-medium">
                  {player.name}
                </span>
                <span className="text-caption text-muted-foreground">
                  {POSITION_LABELS[player.position]}
                </span>
              </div>
              <ConditionBadge condition={player.condition} />
            </li>
          ))}
        </ul>
      )}
      {hasSickReserve && (
        <p className="flex items-center gap-2 rounded-md bg-muted p-2 text-caption text-muted-foreground">
          <Lock className="size-3.5 shrink-0" aria-hidden />
          Doente não pode ser escalado.
        </p>
      )}
    </section>
  );
}

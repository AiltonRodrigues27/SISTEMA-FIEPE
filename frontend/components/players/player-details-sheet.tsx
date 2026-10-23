import { HeartPulse, Pencil, ShoppingCart } from "lucide-react";
import { AttributeBar } from "@/components/players/attribute-bar";
import { ConditionBadge } from "@/components/players/condition-badge";
import { PlayerAvatar } from "@/components/players/player-avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { Player, PlayerAction } from "@/types/players.types";
import { formatMoney } from "@/utils/format";
import { TECHNICAL_ATTRIBUTES } from "@/utils/player-attributes";

type StatCardProps = { label: string; value: string; caption: string };

function StatCard({ label, value, caption }: StatCardProps) {
  return (
    <div className="flex flex-col gap-1 rounded-lg border p-3">
      <span className="text-caption text-muted-foreground">{label}</span>
      <span className="text-display-kpi tabular-nums">{value}</span>
      <span className="text-caption text-muted-foreground">{caption}</span>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between px-3 py-2.5 text-body-sm">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}

type PlayerDetailsSheetProps = {
  player: Player;
  clubName?: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAction?: (action: PlayerAction) => void;
};

export function PlayerDetailsSheet({
  player,
  clubName,
  open,
  onOpenChange,
  onAction,
}: PlayerDetailsSheetProps) {
  const isFree = player.club_id === null;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="overflow-y-auto sm:max-w-md">
        <SheetHeader className="gap-3 border-b">
          <div className="flex items-center gap-3 pr-10">
            <PlayerAvatar id={player.id} name={player.name} />
            <SheetTitle>{player.name}</SheetTitle>
          </div>
          <SheetDescription className="sr-only">
            Detalhes do jogador
          </SheetDescription>
          <div className="flex flex-wrap items-center gap-1.5">
            <Badge variant="outline">{player.position}</Badge>
            <ConditionBadge condition={player.condition} />
            <Badge variant="secondary">{isFree ? "Livre" : clubName}</Badge>
          </div>
        </SheetHeader>
        <div className="flex flex-col gap-5 px-6 py-5">
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              label="Valor de mercado"
              value={formatMoney(player.market_value)}
              caption="Calculado automaticamente"
            />
            <StatCard
              label="Valor base"
              value={formatMoney(player.base_value)}
              caption="Calculado no cadastro"
            />
            <StatCard
              label="Overall"
              value={String(player.overall)}
              caption="Calculado pela posição"
            />
            <StatCard
              label="Potencial"
              value={String(player.potential)}
              caption="Informado no cadastro"
            />
          </div>
          <section className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h3 className="text-body-sm font-medium">Indicadores técnicos</h3>
              <span className="text-caption text-muted-foreground">
                Escala de 1 a 99
              </span>
            </div>
            <div className="flex flex-col gap-2.5">
              {TECHNICAL_ATTRIBUTES.map(({ name, label }) => (
                <AttributeBar
                  key={name}
                  label={label}
                  value={player[name]}
                  potential={player.potential}
                />
              ))}
            </div>
            <p className="flex flex-wrap gap-x-4 gap-y-1 text-caption text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span aria-hidden className="size-2 rounded-full bg-primary" />
                Valor do atributo
              </span>
              <span className="flex items-center gap-1.5">
                <span
                  aria-hidden
                  className="size-2 rounded-full bg-primary/25"
                />
                Até o potencial ({player.potential}), que nenhum atributo passa
              </span>
            </p>
          </section>
          <dl className="divide-y rounded-lg border">
            <InfoRow label="Idade" value={`${player.age} anos`} />
            <InfoRow label="Agilidade" value={String(player.agility)} />
            <InfoRow
              label="Clube"
              value={isFree ? "Livre" : (clubName ?? "—")}
            />
          </dl>
        </div>
        {onAction && (
          <SheetFooter className="flex-row flex-wrap justify-end border-t">
            <Button variant="outline" onClick={() => onAction("edit")}>
              <Pencil aria-hidden />
              Editar
            </Button>
            <Button variant="outline" onClick={() => onAction("condition")}>
              <HeartPulse aria-hidden />
              Alterar condição
            </Button>
            {isFree && (
              <Button onClick={() => onAction("buy")}>
                <ShoppingCart aria-hidden />
                Comprar
              </Button>
            )}
          </SheetFooter>
        )}
      </SheetContent>
    </Sheet>
  );
}

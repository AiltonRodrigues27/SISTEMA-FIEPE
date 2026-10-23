"use client";

import { Lock } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { changePlayerConditionAction } from "@/actions/players.actions";
import { ConditionBadge } from "@/components/players/condition-badge";
import { PlayerSummaryCard } from "@/components/players/player-summary-card";
import { AlertBanner } from "@/components/shared/alert-banner";
import { SubmitButton } from "@/components/shared/submit-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Player, PlayerCondition } from "@/types/players.types";
import { formatMoney } from "@/utils/format";
import { CONDITION_LABELS } from "@/utils/labels";

const OPTIONS: { value: PlayerCondition; description: string }[] = [
  { value: "APTO", description: "Sem desconto por condição." },
  {
    value: "MAL_CONDICIONADO",
    description:
      "Desconto de 15%. Agilidade de 80 a 100 corta pela metade; de 1 a 30 soma 10 pontos.",
  },
  {
    value: "DOENTE",
    description: "Desconto de 30%, com o mesmo ajuste de agilidade.",
  },
];

const STARTERS_COUNT = 5;

type ConditionFormProps = {
  player: Player;
  isStarter: boolean;
  clubName?: string;
  onDone: () => void;
};

function ConditionForm({
  player,
  isStarter,
  clubName,
  onDone,
}: ConditionFormProps) {
  const [selected, setSelected] = useState<PlayerCondition>(player.condition);
  const willLeaveLineup =
    isStarter && selected === "DOENTE" && player.condition !== "DOENTE";

  async function handleSubmit(formData: FormData) {
    const result = await changePlayerConditionAction(player.id, formData);

    if (result.ok) {
      toast.success(result.message, {
        description: `${player.name} agora está ${CONDITION_LABELS[result.data.condition]}. Valor de mercado: ${formatMoney(result.data.market_value)}.`,
      });
      onDone();
      return;
    }
    toast.error(result.message);
  }

  return (
    <form action={handleSubmit} className="grid gap-4">
      <PlayerSummaryCard
        player={player}
        trailing={<ConditionBadge condition={player.condition} />}
      />
      <div className="grid gap-2">
        {OPTIONS.map((option) => {
          const isBlocked =
            player.condition === "DOENTE" && option.value === "APTO";

          return (
            <label
              key={option.value}
              className="flex cursor-pointer gap-3 rounded-lg border p-3 has-checked:border-primary has-checked:bg-primary-soft has-focus-visible:ring-3 has-focus-visible:ring-ring/50 has-disabled:cursor-not-allowed has-disabled:opacity-60"
            >
              <input
                type="radio"
                name="condition"
                value={option.value}
                checked={selected === option.value}
                disabled={isBlocked}
                onChange={() => setSelected(option.value)}
                className="mt-1 accent-primary"
              />
              <span className="flex flex-col gap-0.5">
                <span className="flex items-center gap-2 text-body-sm font-medium">
                  {CONDITION_LABELS[option.value]}
                  {player.condition === option.value && (
                    <Badge variant="secondary">Atual</Badge>
                  )}
                </span>
                <span className="text-caption text-muted-foreground">
                  {option.description}
                </span>
                {isBlocked && (
                  <span className="flex items-center gap-1 text-caption text-muted-foreground">
                    <Lock className="size-3" aria-hidden />
                    De Doente não passa direto para Apto.
                  </span>
                )}
              </span>
            </label>
          );
        })}
      </div>
      {willLeaveLineup && (
        <AlertBanner variant="warning" title={`${player.name} é titular`}>
          Ao passar a Doente, ele sai da escalação, e o {clubName ?? "clube"} só
          volta a jogar partidas depois de escalar de novo os {STARTERS_COUNT}{" "}
          titulares.
        </AlertBanner>
      )}
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onDone}>
          Cancelar
        </Button>
        <SubmitButton
          pendingLabel="Salvando…"
          disabled={selected === player.condition}
        >
          Salvar condição
        </SubmitButton>
      </DialogFooter>
    </form>
  );
}

type ChangeConditionDialogProps = {
  player: Player;
  isStarter: boolean;
  clubName?: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function ChangeConditionDialog({
  player,
  isStarter,
  clubName,
  open,
  onOpenChange,
}: ChangeConditionDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Alterar condição física</DialogTitle>
          <DialogDescription>
            A condição muda o desconto do valor de mercado, recalculado ao
            salvar.
          </DialogDescription>
        </DialogHeader>
        <ConditionForm
          player={player}
          isStarter={isStarter}
          clubName={clubName}
          onDone={() => onOpenChange(false)}
        />
      </DialogContent>
    </Dialog>
  );
}

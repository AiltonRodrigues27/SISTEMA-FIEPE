import { Check, Eye } from "lucide-react";
import { ResultRow } from "@/components/shared/result-row";
import { Button } from "@/components/ui/button";
import {
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Player } from "@/types/players.types";
import { formatMoney } from "@/utils/format";
import { POSITION_LABELS } from "@/utils/labels";

type PlayerCreatedResultProps = {
  player: Player;
  onShowDetails: () => void;
  onClose: () => void;
};

export function PlayerCreatedResult({
  player,
  onShowDetails,
  onClose,
}: PlayerCreatedResultProps) {
  return (
    <>
      <DialogHeader>
        <span className="mb-1 flex size-9 items-center justify-center rounded-full bg-success-soft text-success-soft-foreground">
          <Check className="size-4" aria-hidden />
        </span>
        <DialogTitle>Jogador cadastrado</DialogTitle>
        <DialogDescription>
          {player.name} entrou livre e Apto. Valores em moedas, calculados pela
          API ao salvar.
        </DialogDescription>
      </DialogHeader>
      <dl className="divide-y overflow-hidden rounded-lg border">
        <ResultRow
          title="Valor base"
          caption="Calculado no cadastro: não muda depois"
          value={formatMoney(player.base_value)}
          variant="total"
        />
        <ResultRow
          title="Valor de mercado"
          caption="Com condição, agilidade e idade"
          value={formatMoney(player.market_value)}
        />
        <ResultRow
          title="Overall"
          caption={`Pesos da posição ${POSITION_LABELS[player.position]}`}
          value={String(player.overall)}
        />
      </dl>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onShowDetails}>
          <Eye aria-hidden />
          Ver detalhes
        </Button>
        <Button type="button" onClick={onClose}>
          Fechar
        </Button>
      </DialogFooter>
    </>
  );
}

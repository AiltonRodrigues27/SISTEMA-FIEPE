"use client";

import { HandCoins, Info } from "lucide-react";
import { useState } from "react";
import { sellPlayerAction } from "@/actions/market.actions";
import { PenaltyBadge } from "@/components/market/penalty-badge";
import { PlayerSummaryCard } from "@/components/players/player-summary-card";
import { AlertBanner } from "@/components/shared/alert-banner";
import { CancelButton } from "@/components/shared/cancel-button";
import { ResultRow } from "@/components/shared/result-row";
import { SendingNote } from "@/components/shared/sending-note";
import { SubmitButton } from "@/components/shared/submit-button";
import {
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { SquadMember } from "@/types/clubs.types";
import type { Sale } from "@/types/market.types";
import { formatDate, formatMoney, formatTime } from "@/utils/format";

const STARTERS_COUNT = 5;

type SellFormProps = {
  member: SquadMember;
  clubName: string;
  isStarter: boolean;
  onSold: (sale: Sale) => void;
  onClose: () => void;
};

export function SellForm({
  member,
  clubName,
  isStarter,
  onSold,
  onClose,
}: SellFormProps) {
  const [refusedMessage, setRefusedMessage] = useState<string | null>(null);

  async function handleSell() {
    const result = await sellPlayerAction(member.id);

    if (result.ok) {
      onSold(result.data);
      return;
    }
    setRefusedMessage(result.message);
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>Vender {member.name}?</DialogTitle>
        <DialogDescription>
          O jogador sai do elenco do {clubName} e volta a ficar livre.
        </DialogDescription>
      </DialogHeader>
      <form action={handleSell} className="grid gap-4">
        {refusedMessage && (
          <AlertBanner variant="danger" title="A venda foi recusada">
            {refusedMessage}
          </AlertBanner>
        )}
        {isStarter && (
          <AlertBanner variant="warning" title={`${member.name} é titular`}>
            Ao vender, ele sai da escalação, e o {clubName} só volta a jogar
            partidas depois de escalar de novo os {STARTERS_COUNT} titulares.
          </AlertBanner>
        )}
        <PlayerSummaryCard
          player={member}
          trailing={
            <div className="flex flex-col items-end">
              <span className="text-caption text-muted-foreground">
                Valor de mercado
              </span>
              <span className="text-heading-card tabular-nums">
                {formatMoney(member.market_value)}
              </span>
            </div>
          }
        />
        {member.contract && (
          <dl className="divide-y overflow-hidden rounded-lg border">
            <ResultRow
              title="Valor de compra"
              value={formatMoney(member.contract.purchase_value)}
            />
            <ResultRow
              title="Fim da fidelidade"
              value={`${formatDate(member.contract.loyalty_until)}, ${formatTime(member.contract.loyalty_until)}`}
            />
            <ResultRow
              title="Dias restantes"
              value={member.contract.remaining_days}
            />
            <ResultRow
              title="% de multa se vender agora"
              value={<PenaltyBadge rate={member.contract.penalty_rate} />}
            />
          </dl>
        )}
        <p className="flex items-start gap-2 rounded-lg border bg-muted-subtle p-3 text-caption text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" aria-hidden />A venda é
          pelo valor de mercado do momento. Multa (teto de 10,00), lucro,
          comissão e crédito são calculados ao confirmar.
        </p>
        <SendingNote>
          Enviando a venda. Os botões ficam desabilitados até a resposta.
        </SendingNote>
        <DialogFooter>
          <CancelButton onClick={onClose} />
          <SubmitButton pendingLabel="Vendendo…">
            <HandCoins aria-hidden />
            Confirmar venda
          </SubmitButton>
        </DialogFooter>
      </form>
    </>
  );
}

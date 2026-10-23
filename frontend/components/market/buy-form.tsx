"use client";

import { Info, RefreshCw, Shield, ShoppingCart } from "lucide-react";
import { useState } from "react";
import { buyPlayerAction } from "@/actions/market.actions";
import { PlayerSummaryCard } from "@/components/players/player-summary-card";
import { AlertBanner } from "@/components/shared/alert-banner";
import { CancelButton } from "@/components/shared/cancel-button";
import { FormField } from "@/components/shared/form-field";
import { SendingNote } from "@/components/shared/sending-note";
import { SubmitButton } from "@/components/shared/submit-button";
import {
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Refusal } from "@/types/action.types";
import type { ClubOption } from "@/types/clubs.types";
import type { Purchase } from "@/types/market.types";
import type { Player } from "@/types/players.types";
import { formatMoney } from "@/utils/format";

type BuyFormProps = {
  player: Player;
  clubs: ClubOption[];
  onPurchased: (purchase: Purchase) => void;
  onClose: () => void;
};

export function BuyForm({
  player,
  clubs,
  onPurchased,
  onClose,
}: BuyFormProps) {
  const [clubId, setClubId] = useState<string | null>(null);
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [refusal, setRefusal] = useState<Refusal | null>(null);

  const clubItems = clubs.map((club) => ({
    value: String(club.id),
    label: `${club.name} (${club.acronym}) · caixa ${formatMoney(club.cash)}`,
  }));
  const selectedClub = clubs.find((club) => String(club.id) === clubId);

  async function handleSubmit(formData: FormData) {
    const result = await buyPlayerAction(player.id, formData);

    if (result.ok) {
      onPurchased(result.data);
      return;
    }

    setFieldErrors(result.fieldErrors ?? {});
    if (result.fieldErrors) {
      setRefusal(null);
    } else if (result.isNetworkError) {
      setRefusal({
        title: "Sem conexão",
        message:
          "A compra não foi confirmada. Verifique a conexão e tente de novo.",
        isNetworkError: true,
      });
    } else {
      setRefusal({
        title: "Compra recusada",
        message: result.message,
        isNetworkError: false,
      });
    }
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>Comprar jogador</DialogTitle>
        <DialogDescription>
          Escolha o clube comprador e até quando vai a fidelidade do contrato.
        </DialogDescription>
      </DialogHeader>
      <form action={handleSubmit} className="grid gap-4">
        {refusal && (
          <AlertBanner variant="danger" title={refusal.title}>
            {refusal.message}
          </AlertBanner>
        )}
        <PlayerSummaryCard
          player={player}
          trailing={
            <div className="flex flex-col items-end">
              <span className="text-caption text-muted-foreground">
                Valor de mercado
              </span>
              <span className="text-heading-card tabular-nums">
                {formatMoney(player.market_value)}
              </span>
            </div>
          }
        />
        <FormField
          id="club_id"
          label="Clube comprador"
          error={fieldErrors.club_id}
          hint={
            selectedClub
              ? `Caixa atual: ${formatMoney(selectedClub.cash)}. O custo total (valor + taxa) pode ir até 50% do caixa.`
              : "O custo total (valor + taxa) pode ir até 50% do caixa do clube."
          }
        >
          <Select
            name="club_id"
            items={clubItems}
            value={clubId}
            onValueChange={setClubId}
          >
            <SelectTrigger
              id="club_id"
              className="h-9 w-full"
              aria-invalid={fieldErrors.club_id ? true : undefined}
            >
              <Shield className="text-muted-foreground" aria-hidden />
              <SelectValue placeholder="Escolha o clube" />
            </SelectTrigger>
            <SelectContent>
              {clubItems.map((item) => (
                <SelectItem key={item.value} value={item.value}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </FormField>
        <FormField
          id="loyalty_date"
          label="Fim da fidelidade"
          error={fieldErrors.loyalty_until}
          hint="Depois do momento da compra e até 1.095 dias. Horário de Brasília, enviado com o fuso (-03:00)."
        >
          <div className="grid grid-cols-[1fr_8rem] gap-2">
            <Input
              id="loyalty_date"
              type="date"
              value={date}
              onChange={(event) => setDate(event.target.value)}
              aria-invalid={fieldErrors.loyalty_until ? true : undefined}
            />
            <Input
              id="loyalty_time"
              type="time"
              aria-label="Hora do fim da fidelidade"
              value={time}
              onChange={(event) => setTime(event.target.value)}
              aria-invalid={fieldErrors.loyalty_until ? true : undefined}
            />
          </div>
          <input
            type="hidden"
            name="loyalty_until"
            value={date && time ? `${date}T${time}` : ""}
          />
        </FormField>
        <p className="flex items-start gap-2 rounded-lg border bg-muted-subtle p-3 text-caption text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" aria-hidden />A taxa é de
          5% do valor de mercado, só quando ele passa de 30,00. Taxa, custo e
          novo caixa são calculados ao confirmar.
        </p>
        <SendingNote>
          Enviando a compra. Os botões ficam desabilitados até a resposta.
        </SendingNote>
        <DialogFooter>
          <CancelButton onClick={onClose} />
          <SubmitButton pendingLabel="Comprando…">
            {refusal?.isNetworkError ? (
              <>
                <RefreshCw aria-hidden />
                Tentar de novo
              </>
            ) : (
              <>
                <ShoppingCart aria-hidden />
                Confirmar compra
              </>
            )}
          </SubmitButton>
        </DialogFooter>
      </form>
    </>
  );
}

"use client";

import { Info, Lock, User } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import {
  createPlayerAction,
  updatePlayerAction,
} from "@/actions/players.actions";
import { AttributePreview } from "@/components/players/attribute-preview";
import { LockedField } from "@/components/players/locked-field";
import { PositionCards } from "@/components/players/position-cards";
import { AlertBanner } from "@/components/shared/alert-banner";
import { FormField } from "@/components/shared/form-field";
import { SubmitButton } from "@/components/shared/submit-button";
import { Button } from "@/components/ui/button";
import {
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { Player, PlayerFormValues } from "@/types/players.types";
import { formatMoney } from "@/utils/format";
import { TECHNICAL_ATTRIBUTES } from "@/utils/player-attributes";

function getInitialValues(player?: Player): PlayerFormValues {
  return {
    name: player?.name ?? "",
    position: player?.position ?? "",
    age: player ? String(player.age) : "",
    agility: player ? String(player.agility) : "",
  };
}

type NumberFieldProps = {
  name: string;
  label: string;
  min: number;
  max: number;
  value: string;
  hint?: string;
  error?: string;
  onChange: (name: string, value: string) => void;
};

function NumberField({
  name,
  label,
  min,
  max,
  value,
  hint,
  error,
  onChange,
}: NumberFieldProps) {
  return (
    <FormField id={name} label={label} hint={hint} error={error}>
      <Input
        id={name}
        name={name}
        type="number"
        inputMode="numeric"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(name, event.target.value)}
        aria-invalid={error ? true : undefined}
        aria-describedby={error || hint ? `${name}-message` : undefined}
      />
    </FormField>
  );
}

type PlayerFormProps = {
  player?: Player;
  onCreated: (player: Player) => void;
  onClose: () => void;
};

export function PlayerForm({ player, onCreated, onClose }: PlayerFormProps) {
  const isEditing = player !== undefined;
  const isPositionLocked = player !== undefined && player.club_id !== null;
  const [values, setValues] = useState(() => getInitialValues(player));
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [refusedMessage, setRefusedMessage] = useState<string | null>(null);

  function setField(name: string, value: string) {
    setValues((current) => ({ ...current, [name]: value }));
  }

  function showRefusal(result: {
    message: string;
    fieldErrors?: Record<string, string>;
  }) {
    setFieldErrors(result.fieldErrors ?? {});
    setRefusedMessage(result.fieldErrors ? null : result.message);
    toast.error(result.message);
  }

  async function handleSubmit(formData: FormData) {
    if (player) {
      const result = await updatePlayerAction(player.id, formData);
      if (!result.ok) return showRefusal(result);

      toast.success(result.message);
      onClose();
      return;
    }

    const result = await createPlayerAction(formData);
    if (!result.ok) return showRefusal(result);

    onCreated(result.data);
  }

  const numberField = (name: string, min: number, max: number) => ({
    name,
    min,
    max,
    value: values[name] ?? "",
    error: fieldErrors[name],
    onChange: setField,
  });
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;

  return (
    <>
      <DialogHeader>
        <DialogTitle>
          {isEditing ? "Editar jogador" : "Novo jogador"}
        </DialogTitle>
        <DialogDescription>
          {hasFieldErrors
            ? "Corrija os campos destacados para salvar."
            : isEditing
              ? "Edite nome, posição, idade e agilidade. Os demais dados não mudam."
              : "Preencha os dados e os indicadores técnicos. O valor base, o overall e o valor de mercado são calculados ao salvar."}
        </DialogDescription>
      </DialogHeader>
      <form action={handleSubmit} className="grid gap-4">
        {refusedMessage && (
          <AlertBanner
            variant="danger"
            title="Não foi possível salvar o jogador"
          >
            {refusedMessage}
          </AlertBanner>
        )}
        <FormField
          id="name"
          label="Nome"
          error={fieldErrors.name}
          hint="De 3 a 100 caracteres, com pelo menos duas palavras e sem números."
        >
          <div className="relative">
            <User
              className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden
            />
            <Input
              id="name"
              name="name"
              value={values.name}
              onChange={(event) => setField("name", event.target.value)}
              maxLength={100}
              placeholder="Ex.: Lucas Almeida"
              className="pl-9"
              aria-invalid={fieldErrors.name ? true : undefined}
              aria-describedby="name-message"
            />
          </div>
        </FormField>
        <PositionCards
          value={values.position}
          onChange={(position) => setField("position", position)}
          isLocked={isPositionLocked}
          error={fieldErrors.position}
        />
        <div
          className={cn(
            "grid gap-4",
            player ? "sm:grid-cols-2" : "sm:grid-cols-3",
          )}
        >
          <NumberField
            {...numberField("age", 16, 45)}
            label="Idade"
            hint={
              player
                ? `De 16 a 45, sem diminuir (atual: ${player.age}).`
                : "De 16 a 45 anos."
            }
          />
          <NumberField
            {...numberField("agility", 1, 100)}
            label="Agilidade"
            hint="De 1 a 100 (até 85 com 35 anos ou mais)."
          />
          {!player && (
            <LockedField
              label="Valor base (moedas)"
              hint="Calculado no cadastro."
            />
          )}
        </div>
        {player ? (
          <p className="flex items-center gap-2 rounded-lg border bg-muted-subtle p-3 text-caption text-muted-foreground">
            <Lock className="size-3.5 shrink-0" aria-hidden />
            Não mudam depois do cadastro: valor base (
            {formatMoney(player.base_value)}), indicadores e potencial.
          </p>
        ) : (
          <fieldset className="grid gap-3 border-t pt-4">
            <legend className="sr-only">Indicadores técnicos</legend>
            <div className="flex flex-col gap-1">
              <h3 className="text-body-sm font-medium">Indicadores técnicos</h3>
              <p className="text-caption text-muted-foreground">
                Seis atributos e o potencial, de 1 a 99. Não mudam depois do
                cadastro; a soma dos seis atributos não pode passar de 480.
              </p>
            </div>
            <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_14rem]">
              <div className="grid grid-cols-2 content-start gap-4 sm:grid-cols-4">
                {TECHNICAL_ATTRIBUTES.map(({ name, label }) => (
                  <NumberField
                    key={name}
                    {...numberField(name, 1, 99)}
                    label={label}
                  />
                ))}
                <NumberField
                  {...numberField("potential", 1, 99)}
                  label="Potencial"
                  hint="≥ maior atributo; igual a ele com 33+ anos"
                />
                <LockedField
                  label="Overall"
                  hint="Calculado automaticamente."
                />
              </div>
              <AttributePreview draft={values} />
            </div>
          </fieldset>
        )}
        <div className="flex flex-col gap-3 border-t pt-4 sm:flex-row sm:items-center sm:justify-between">
          {player ? (
            <span />
          ) : (
            <p className="flex items-center gap-2 text-caption text-muted-foreground">
              <Info className="size-3.5 shrink-0" aria-hidden />O jogador começa
              livre e Apto.
            </p>
          )}
          <div className="flex flex-col-reverse gap-2 sm:flex-row">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <SubmitButton pendingLabel="Salvando…">
              {isEditing ? "Salvar alterações" : "Salvar jogador"}
            </SubmitButton>
          </div>
        </div>
      </form>
    </>
  );
}

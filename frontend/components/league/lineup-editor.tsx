"use client";

import { Check, CircleCheck, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { setLineupAction } from "@/actions/lineup.actions";
import { FormationPicker } from "@/components/league/formation-picker";
import { LineupTable } from "@/components/league/lineup-table";
import { PitchPreview } from "@/components/league/pitch-preview";
import { ReservesCard } from "@/components/league/reserves-card";
import { AlertBanner } from "@/components/shared/alert-banner";
import { SubmitButton } from "@/components/shared/submit-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type {
  Formation,
  Lineup,
  LineupRow,
  LineupSlot,
} from "@/types/league.types";
import type { Player } from "@/types/players.types";
import { pluralize } from "@/utils/format";
import { buildLineupSlots } from "@/utils/formations";
import { getLineIndexes, getUsedAttributes } from "@/utils/lineup-attributes";

const DEFAULT_FORMATION: Formation = "2-1-1";
const STARTERS_COUNT = 5;

const listFormatter = new Intl.ListFormat("pt-BR", {
  style: "long",
  type: "conjunction",
});

function pickInitialStarters(lineup: Lineup): Record<string, string> {
  if (!lineup.formation) return {};

  const remaining = [...lineup.players];
  const starters: Record<string, string> = {};

  for (const slot of buildLineupSlots(lineup.formation)) {
    const index = remaining.findIndex((player) =>
      slot.positions.includes(player.position),
    );
    if (index >= 0) {
      starters[slot.key] = String(remaining.splice(index, 1)[0].id);
    }
  }
  return starters;
}

function getOptionsForSlot(
  slot: LineupSlot,
  squad: Player[],
  starters: Record<string, string>,
) {
  const takenByOtherSlots = new Set(
    Object.entries(starters)
      .filter(([key]) => key !== slot.key)
      .map(([, id]) => id),
  );

  return squad
    .filter(
      (player) =>
        slot.positions.includes(player.position) &&
        player.condition !== "DOENTE" &&
        !takenByOtherSlots.has(String(player.id)),
    )
    .map((player) => ({
      value: String(player.id),
      label: `${player.name} (${player.position})`,
    }));
}

function LineupStatus({ isComplete }: { isComplete: boolean }) {
  if (isComplete) {
    return (
      <Badge variant="success">
        <CircleCheck aria-hidden />
        Completa
      </Badge>
    );
  }
  return (
    <Badge variant="warning">
      <TriangleAlert aria-hidden />
      Incompleta
    </Badge>
  );
}

type LineupEditorProps = {
  clubId: number;
  clubName: string;
  squad: Player[];
  lineup: Lineup;
};

export function LineupEditor({
  clubId,
  clubName,
  squad,
  lineup,
}: LineupEditorProps) {
  const [formation, setFormation] = useState<Formation>(
    lineup.formation ?? DEFAULT_FORMATION,
  );
  const [starters, setStarters] = useState(() => pickInitialStarters(lineup));
  const [refusedMessage, setRefusedMessage] = useState<string | null>(null);

  const slots = buildLineupSlots(formation);
  const squadById = new Map(squad.map((player) => [String(player.id), player]));
  const playerOf = (slot: LineupSlot) =>
    squadById.get(starters[slot.key] ?? "");
  const lineSlots = slots.filter((slot) => !slot.positions.includes("GOL"));
  const lineIndexes = getLineIndexes(lineSlots.map(playerOf));

  const rows: LineupRow[] = slots.map((slot) => {
    const player = playerOf(slot);
    const lineSlotIndex = lineSlots.indexOf(slot);

    return {
      slot,
      player,
      selectedId: starters[slot.key] || null,
      options: getOptionsForSlot(slot, squad, starters),
      attributes: player
        ? getUsedAttributes(
            player,
            lineSlotIndex >= 0 ? lineIndexes[lineSlotIndex] : null,
          )
        : [],
    };
  });

  const selectedIds = new Set(rows.map((row) => row.selectedId));
  const reserves = squad.filter(
    (player) => !selectedIds.has(String(player.id)),
  );
  const weakPlayers = rows.flatMap(({ player }) =>
    player?.condition === "MAL_CONDICIONADO" ? [player] : [],
  );
  const isReadyToSave = rows.every((row) => row.selectedId !== null);

  function handleFormationChange(next: Formation) {
    const nextKeys = new Set(buildLineupSlots(next).map((slot) => slot.key));
    setFormation(next);
    setStarters((current) =>
      Object.fromEntries(
        Object.entries(current).filter(([key]) => nextKeys.has(key)),
      ),
    );
  }

  function handleStarterChange(slotKey: string, playerId: string | null) {
    setStarters((current) => ({ ...current, [slotKey]: playerId ?? "" }));
  }

  function resetToSaved() {
    setFormation(lineup.formation ?? DEFAULT_FORMATION);
    setStarters(pickInitialStarters(lineup));
    setRefusedMessage(null);
  }

  async function handleSubmit(formData: FormData) {
    const result = await setLineupAction(clubId, formData);

    if (result.ok) {
      setRefusedMessage(null);
      toast.success(result.message, {
        description: `${clubName} na ${result.data.formation}, com os ${result.data.players.length} titulares devolvidos pela API.`,
      });
      return;
    }
    setRefusedMessage(result.message);
    toast.error(result.message);
  }

  return (
    <form
      action={handleSubmit}
      className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start"
    >
      <section className="overflow-hidden rounded-xl border bg-card shadow-xs">
        <div className="flex flex-col gap-4 p-4">
          <header className="flex items-start justify-between gap-3">
            <div className="flex flex-col gap-1">
              <h2 className="text-heading-card">Titulares</h2>
              <p className="text-caption text-muted-foreground">
                1 goleiro e 4 jogadores de linha, na formação escolhida. Salvar
                troca os {STARTERS_COUNT} de uma vez.
              </p>
            </div>
            <LineupStatus isComplete={lineup.complete} />
          </header>
          {refusedMessage && (
            <AlertBanner variant="danger" title="A escalação foi recusada">
              {refusedMessage}
            </AlertBanner>
          )}
          {!lineup.complete && (
            <AlertBanner
              variant="warning"
              title={`Escalação incompleta: o ${clubName} não pode jogar partidas`}
            >
              {squad.length < STARTERS_COUNT
                ? `O elenco tem ${squad.length} ${pluralize(squad.length, "jogador", "jogadores")}, e a escalação precisa de ${STARTERS_COUNT}: 1 goleiro e 4 jogadores de linha. Compre jogadores e salve a escalação com os ${STARTERS_COUNT} titulares.`
                : lineup.formation
                  ? `A formação ${lineup.formation} continua salva com ${lineup.players.length} de ${STARTERS_COUNT} titulares, porque um titular foi vendido ou ficou doente. O clube só volta a jogar depois de escalar de novo.`
                  : `Escolha a formação e os ${STARTERS_COUNT} titulares para o clube poder jogar partidas.`}
            </AlertBanner>
          )}
          <FormationPicker value={formation} onChange={handleFormationChange} />
        </div>
        <LineupTable rows={rows} onChange={handleStarterChange} />
        {weakPlayers.length > 0 && (
          <div className="p-4">
            <AlertBanner
              variant="warning"
              title={`${listFormatter.format(weakPlayers.map((player) => player.name))} ${weakPlayers.length > 1 ? "estão mal condicionados" : "está mal condicionado"}`}
            >
              Podem jogar, mas cada atributo vale 15% a menos durante a partida.
            </AlertBanner>
          </div>
        )}
        <footer className="flex flex-col gap-3 border-t p-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-caption text-muted-foreground">
            A escalação vale até ser trocada. Titular vendido ou que fica doente
            sai dela, e o clube só volta a jogar depois de escalar de novo.
          </p>
          <div className="flex gap-2 sm:shrink-0">
            <Button type="button" variant="outline" onClick={resetToSaved}>
              Cancelar
            </Button>
            <SubmitButton pendingLabel="Salvando…" disabled={!isReadyToSave}>
              <Check aria-hidden />
              Salvar escalação
            </SubmitButton>
          </div>
        </footer>
      </section>
      <div className="flex flex-col gap-4">
        <PitchPreview formation={formation} rows={rows} />
        <ReservesCard reserves={reserves} squadCount={squad.length} />
      </div>
    </form>
  );
}

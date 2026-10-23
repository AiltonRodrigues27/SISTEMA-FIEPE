import { Plus, Swords } from "lucide-react";
import type { Formation, LineupRow, LineupSlot } from "@/types/league.types";
import type { Player } from "@/types/players.types";
import { getInitials } from "@/utils/format";

const LINES_FROM_ATTACK_TO_GOAL = ["at", "mf", "df", "gk"];

const PITCH_STRIPES =
  "repeating-linear-gradient(180deg, rgb(255 255 255 / 0.06) 0 32px, transparent 32px 64px)";

function describeEmptySlots(emptyCount: number): string {
  if (emptyCount === 0) return ", do goleiro ao ataque.";
  if (emptyCount === 1) return "; a vaga vazia fica tracejada.";
  return "; as vagas vazias ficam tracejadas.";
}

function PitchLines() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-2 rounded border border-white/40"
    >
      <span className="absolute top-1/2 left-0 w-full border-t border-white/40" />
      <span className="absolute top-1/2 left-1/2 size-14 -translate-1/2 rounded-full border border-white/40" />
      <span className="absolute top-0 left-1/2 h-8 w-20 -translate-x-1/2 border border-t-0 border-white/40" />
      <span className="absolute bottom-0 left-1/2 h-12 w-32 -translate-x-1/2 border border-b-0 border-white/40" />
    </div>
  );
}

function PlayerBubble({ slot, player }: { slot: LineupSlot; player?: Player }) {
  if (!player) {
    return (
      <div className="flex flex-col items-center gap-0.5">
        <span className="flex size-8 items-center justify-center rounded-full border border-dashed border-white/70 text-white/70">
          <Plus className="size-3.5" aria-hidden />
        </span>
        <span className="text-caption text-white/70">{slot.label}</span>
      </div>
    );
  }

  return (
    <div className="relative flex flex-col items-center gap-0.5">
      <span className="flex size-8 items-center justify-center rounded-full bg-primary text-caption font-medium text-primary-foreground ring-2 ring-white">
        {getInitials(player.name)}
      </span>
      {player.condition === "MAL_CONDICIONADO" && (
        <span
          role="img"
          aria-label="Mal condicionado"
          className="absolute -top-1 right-0 size-3 rounded-full bg-orange-400 ring-2 ring-white"
        />
      )}
      <span className="max-w-20 truncate text-caption text-white">
        {player.name.split(" ").at(-1)}
      </span>
    </div>
  );
}

type PitchPreviewProps = {
  formation: Formation;
  rows: LineupRow[];
};

export function PitchPreview({ formation, rows }: PitchPreviewProps) {
  return (
    <section className="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-xs">
      <div className="flex flex-col gap-1">
        <h2 className="text-heading-card">Em campo</h2>
        <p className="text-caption text-muted-foreground">
          Prévia da formação {formation}
          {describeEmptySlots(rows.filter(({ player }) => !player).length)}
        </p>
      </div>
      <div
        className="relative flex min-h-64 flex-col justify-around overflow-hidden rounded-lg bg-emerald-800 p-4"
        style={{ backgroundImage: PITCH_STRIPES }}
      >
        <PitchLines />
        {LINES_FROM_ATTACK_TO_GOAL.map((line) => {
          const lineRows = rows.filter(({ slot }) => slot.key.startsWith(line));
          if (lineRows.length === 0) return null;

          return (
            <div key={line} className="relative flex justify-around">
              {lineRows.map(({ slot, player }) => (
                <PlayerBubble key={slot.key} slot={slot} player={player} />
              ))}
            </div>
          );
        })}
      </div>
      <p className="flex gap-2 text-caption text-muted-foreground">
        <Swords className="mt-0.5 size-3.5 shrink-0" aria-hidden />
        Na partida, atacam os 3 jogadores de linha mais avançados e defendem o
        goleiro e os 2 mais recuados. É gol quando o ataque é maior que a
        defesa.
      </p>
    </section>
  );
}

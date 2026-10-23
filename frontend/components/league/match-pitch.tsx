import { Goal } from "lucide-react";
import { cn } from "@/lib/utils";
import type {
  MatchDetail,
  MatchSide,
  PitchPlayer,
  TeamSide,
} from "@/types/matches.types";
import { getInitials } from "@/utils/format";
import { buildTeamLineup } from "@/utils/match-lineups";

const SLOT_POSITIONS = {
  goalkeeper: { x: 7, y: 50 },
  1: { x: 22, y: 28 },
  2: { x: 22, y: 72 },
  3: { x: 37, y: 50 },
  4: { x: 47, y: 50 },
};

const SHORT_ATTRIBUTES: Record<string, string> = {
  shooting: "Fin",
  passing: "Pas",
  dribbling: "Dr",
  defending: "Def",
};

const PITCH_STRIPES =
  "repeating-linear-gradient(90deg, rgb(255 255 255 / 0.05) 0 48px, transparent 48px 96px)";

function describeValues(player: PitchPlayer): string {
  const parts = [player.position];
  if (player.attack) {
    parts.push(
      `${SHORT_ATTRIBUTES[player.attack.attribute] ?? player.attack.attribute} ${player.attack.value}`,
    );
  }
  if (player.defense !== undefined) parts.push(`Def ${player.defense}`);

  return parts.join(" · ");
}

function PitchLines() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-3 rounded border border-white/40"
    >
      <span className="absolute inset-y-0 left-1/2 border-l border-white/40" />
      <span className="absolute top-1/2 left-1/2 size-20 -translate-1/2 rounded-full border border-white/40" />
      <span className="absolute top-1/2 left-0 h-1/2 w-[14%] -translate-y-1/2 border-y border-r border-white/40" />
      <span className="absolute top-1/2 right-0 h-1/2 w-[14%] -translate-y-1/2 border-y border-l border-white/40" />
    </div>
  );
}

function PitchBubble({
  player,
  side,
}: {
  player: PitchPlayer;
  side: TeamSide;
}) {
  const slot = SLOT_POSITIONS[player.line ?? "goalkeeper"];
  const x = side === "home" ? slot.x : 100 - slot.x;

  return (
    <div
      className="absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-0.5 text-center"
      style={{ left: `${x}%`, top: `${slot.y}%` }}
    >
      <span className="relative">
        <span
          className={cn(
            "flex size-9 items-center justify-center rounded-full text-caption font-medium ring-2 ring-white",
            side === "home"
              ? "bg-primary text-primary-foreground"
              : "bg-white text-foreground",
          )}
        >
          {getInitials(player.name)}
        </span>
        {player.condition === "MAL_CONDICIONADO" && (
          <span
            role="img"
            aria-label="Mal condicionado"
            className="absolute -top-1 -left-1 size-3 rounded-full bg-orange-400 ring-2 ring-white"
          />
        )}
        {player.attack?.scored && (
          <span
            role="img"
            aria-label="Gol no duelo"
            className="absolute -top-2 -right-2 flex size-5 items-center justify-center rounded-full bg-white text-foreground"
          >
            <Goal className="size-3" aria-hidden />
          </span>
        )}
      </span>
      <span className="max-w-28 truncate text-caption font-medium text-white">
        {player.name}
      </span>
      <span className="text-caption whitespace-nowrap text-white/80">
        {describeValues(player)}
      </span>
    </div>
  );
}

function TeamTag({ team, side }: { team: MatchSide; side: TeamSide }) {
  return (
    <span
      className={cn(
        "absolute top-4 flex items-center gap-1.5 rounded-md bg-black/30 px-2 py-0.5 text-caption text-white",
        side === "home" ? "left-5" : "right-5",
      )}
    >
      <span
        aria-hidden
        className={cn(
          "size-2 rounded-full",
          side === "home" ? "bg-primary" : "bg-white",
        )}
      />
      {team.club_name} {team.formation} ·{" "}
      {side === "home" ? "ataca →" : "← ataca"}
    </span>
  );
}

export function MatchPitch({ match }: { match: MatchDetail }) {
  const teams: { side: TeamSide; team: MatchSide }[] = [
    { side: "home", team: match.home },
    { side: "away", team: match.away },
  ];

  return (
    <section className="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-xs">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <h2 className="text-heading-card">Em campo</h2>
          <p className="text-caption text-muted-foreground">
            Titulares de cada clube na formação da partida e os valores usados
            nos duelos, já com o efeito da condição.
          </p>
        </div>
        <ul className="flex items-center gap-4 text-caption text-muted-foreground">
          <li className="flex items-center gap-1.5">
            <span aria-hidden className="size-2.5 rounded-full bg-orange-400" />
            Mal condicionado
          </li>
          <li className="flex items-center gap-1.5">
            <Goal className="size-3.5" aria-hidden />
            Gol no duelo
          </li>
        </ul>
      </div>
      <div className="overflow-x-auto">
        <div
          className="relative aspect-2/1 min-w-176 overflow-hidden rounded-lg bg-emerald-800"
          style={{ backgroundImage: PITCH_STRIPES }}
        >
          <PitchLines />
          {teams.map(({ side, team }) => (
            <TeamTag key={side} team={team} side={side} />
          ))}
          {teams.flatMap(({ side, team }) =>
            buildTeamLineup(match, team.club_id).map((player) => (
              <PitchBubble key={player.id} player={player} side={side} />
            )),
          )}
        </div>
      </div>
    </section>
  );
}

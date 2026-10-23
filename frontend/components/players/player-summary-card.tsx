import type { ReactNode } from "react";
import { PlayerAvatar } from "@/components/players/player-avatar";
import type { Player } from "@/types/players.types";
import { POSITION_LABELS } from "@/utils/labels";

type PlayerSummaryCardProps = {
  player: Player;
  trailing: ReactNode;
};

export function PlayerSummaryCard({
  player,
  trailing,
}: PlayerSummaryCardProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border bg-muted-subtle p-3">
      <PlayerAvatar id={player.id} name={player.name} />
      <div className="flex min-w-0 flex-1 flex-col">
        <span className="truncate text-body-sm font-medium">{player.name}</span>
        <span className="text-caption text-muted-foreground">
          {player.position} · {POSITION_LABELS[player.position]} · {player.age}{" "}
          anos
        </span>
      </div>
      {trailing}
    </div>
  );
}

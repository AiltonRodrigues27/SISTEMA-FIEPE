"use client";

import { useState } from "react";
import { PlayerCreatedResult } from "@/components/players/player-created-result";
import { PlayerDetailsSheet } from "@/components/players/player-details-sheet";
import { PlayerForm } from "@/components/players/player-form";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import type { Player } from "@/types/players.types";

type PlayerFormDialogProps = {
  player?: Player;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function PlayerFormDialog({
  player,
  open,
  onOpenChange,
}: PlayerFormDialogProps) {
  const [created, setCreated] = useState<Player | null>(null);
  const [detailsPlayer, setDetailsPlayer] = useState<Player | null>(null);

  function handleOpenChange(next: boolean) {
    if (!next) setCreated(null);
    onOpenChange(next);
  }

  function showCreatedDetails(createdPlayer: Player) {
    setDetailsPlayer(createdPlayer);
    handleOpenChange(false);
  }

  return (
    <>
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent
          className={cn(
            "max-h-[90svh] overflow-y-auto",
            created ? "sm:max-w-md" : player ? "sm:max-w-xl" : "sm:max-w-3xl",
          )}
        >
          {created ? (
            <PlayerCreatedResult
              player={created}
              onShowDetails={() => showCreatedDetails(created)}
              onClose={() => handleOpenChange(false)}
            />
          ) : (
            <PlayerForm
              player={player}
              onCreated={setCreated}
              onClose={() => handleOpenChange(false)}
            />
          )}
        </DialogContent>
      </Dialog>
      {detailsPlayer && (
        <PlayerDetailsSheet
          player={detailsPlayer}
          open
          onOpenChange={() => setDetailsPlayer(null)}
        />
      )}
    </>
  );
}

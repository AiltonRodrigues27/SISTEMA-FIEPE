"use client";

import { Trash2 } from "lucide-react";
import { toast } from "sonner";
import { deletePlayerAction } from "@/actions/players.actions";
import { PlayerSummaryCard } from "@/components/players/player-summary-card";
import { SubmitButton } from "@/components/shared/submit-button";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import type { Player } from "@/types/players.types";

type DeletePlayerDialogProps = {
  player: Player;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function DeletePlayerDialog({
  player,
  open,
  onOpenChange,
}: DeletePlayerDialogProps) {
  async function handleDelete() {
    const result = await deletePlayerAction(player.id);

    if (result.ok) {
      toast.success(result.message, {
        description: `${player.name} saiu da lista. Transações e partidas antigas dele continuam gravadas.`,
      });
      onOpenChange(false);
      return;
    }
    toast.error(result.message);
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Excluir {player.name}?</AlertDialogTitle>
          <AlertDialogDescription>
            O jogador sai da lista e da busca, mas as transações e as partidas
            antigas dele continuam como foram gravadas.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <PlayerSummaryCard
          player={player}
          trailing={<Badge variant="secondary">Livre</Badge>}
        />
        <form action={handleDelete}>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <SubmitButton variant="destructive" pendingLabel="Excluindo…">
              <Trash2 aria-hidden />
              Excluir jogador
            </SubmitButton>
          </AlertDialogFooter>
        </form>
      </AlertDialogContent>
    </AlertDialog>
  );
}

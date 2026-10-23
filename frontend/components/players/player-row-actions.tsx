"use client";

import {
  Eye,
  HeartPulse,
  MoreHorizontal,
  Pencil,
  ShoppingCart,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { BuyPlayerDialog } from "@/components/market/buy-player-dialog";
import { ChangeConditionDialog } from "@/components/players/change-condition-dialog";
import { DeletePlayerDialog } from "@/components/players/delete-player-dialog";
import { PlayerDetailsSheet } from "@/components/players/player-details-sheet";
import { PlayerFormDialog } from "@/components/players/player-form-dialog";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { ClubOption } from "@/types/clubs.types";
import type { Player, PlayerDialogName } from "@/types/players.types";

type PlayerRowActionsProps = {
  player: Player;
  clubs: ClubOption[];
  isStarter: boolean;
};

export function PlayerRowActions({
  player,
  clubs,
  isStarter,
}: PlayerRowActionsProps) {
  const [openDialog, setOpenDialog] = useState<PlayerDialogName | null>(null);
  const isFree = player.club_id === null;
  const clubName = clubs.find((club) => club.id === player.club_id)?.name;

  function dialogOpenChange(name: PlayerDialogName) {
    return (open: boolean) => setOpenDialog(open ? name : null);
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger
          render={
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={`Ações de ${player.name}`}
            />
          }
        >
          <MoreHorizontal />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-60">
          <DropdownMenuGroup>
            <DropdownMenuLabel>{player.name}</DropdownMenuLabel>
            <DropdownMenuItem onClick={() => setOpenDialog("details")}>
              <Eye aria-hidden />
              Ver detalhes
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setOpenDialog("edit")}>
              <Pencil aria-hidden />
              Editar
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setOpenDialog("condition")}>
              <HeartPulse aria-hidden />
              Alterar condição
            </DropdownMenuItem>
            {isFree && (
              <DropdownMenuItem onClick={() => setOpenDialog("buy")}>
                <ShoppingCart aria-hidden />
                Comprar
              </DropdownMenuItem>
            )}
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem
              variant="destructive"
              disabled={!isFree}
              onClick={() => setOpenDialog("delete")}
            >
              <Trash2 aria-hidden />
              Excluir
            </DropdownMenuItem>
            <p className="px-3 pb-1.5 text-caption text-muted-foreground">
              {isFree
                ? "Disponível porque o jogador está livre."
                : "Só jogador livre pode ser excluído."}
            </p>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
      <PlayerDetailsSheet
        player={player}
        clubName={clubName}
        open={openDialog === "details"}
        onOpenChange={dialogOpenChange("details")}
        onAction={setOpenDialog}
      />
      <PlayerFormDialog
        player={player}
        open={openDialog === "edit"}
        onOpenChange={dialogOpenChange("edit")}
      />
      <ChangeConditionDialog
        player={player}
        isStarter={isStarter}
        clubName={clubName}
        open={openDialog === "condition"}
        onOpenChange={dialogOpenChange("condition")}
      />
      {isFree && (
        <BuyPlayerDialog
          player={player}
          clubs={clubs}
          open={openDialog === "buy"}
          onOpenChange={dialogOpenChange("buy")}
        />
      )}
      <DeletePlayerDialog
        player={player}
        open={openDialog === "delete"}
        onOpenChange={dialogOpenChange("delete")}
      />
    </>
  );
}

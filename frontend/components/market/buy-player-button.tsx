"use client";

import { ShoppingCart } from "lucide-react";
import { useState } from "react";
import { BuyPlayerDialog } from "@/components/market/buy-player-dialog";
import { Button } from "@/components/ui/button";
import type { ClubOption } from "@/types/clubs.types";
import type { Player } from "@/types/players.types";

type BuyPlayerButtonProps = {
  player: Player;
  clubs: ClubOption[];
};

export function BuyPlayerButton({ player, clubs }: BuyPlayerButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setIsOpen(true)}>
        <ShoppingCart aria-hidden />
        Comprar
      </Button>
      <BuyPlayerDialog
        player={player}
        clubs={clubs}
        open={isOpen}
        onOpenChange={setIsOpen}
      />
    </>
  );
}

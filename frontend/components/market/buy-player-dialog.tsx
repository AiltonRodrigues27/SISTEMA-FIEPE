"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { BuyForm } from "@/components/market/buy-form";
import { PurchaseResult } from "@/components/market/purchase-result";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import type { ClubOption } from "@/types/clubs.types";
import type { Purchase } from "@/types/market.types";
import type { Player } from "@/types/players.types";

type BuyPlayerDialogProps = {
  player: Player;
  clubs: ClubOption[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function BuyPlayerDialog({
  player,
  clubs,
  open,
  onOpenChange,
}: BuyPlayerDialogProps) {
  const router = useRouter();
  const [purchase, setPurchase] = useState<Purchase | null>(null);

  function handleOpenChange(next: boolean) {
    if (!next) {
      if (purchase) router.refresh();
      setPurchase(null);
    }
    onOpenChange(next);
  }

  const clubName =
    clubs.find((club) => club.id === purchase?.club_id)?.name ?? "clube";

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[90svh] overflow-y-auto">
        {purchase ? (
          <PurchaseResult
            purchase={purchase}
            clubName={clubName}
            onClose={() => handleOpenChange(false)}
          />
        ) : (
          <BuyForm
            player={player}
            clubs={clubs}
            onPurchased={setPurchase}
            onClose={() => handleOpenChange(false)}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}

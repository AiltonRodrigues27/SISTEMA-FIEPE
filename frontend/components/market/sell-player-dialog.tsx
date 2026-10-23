"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { SaleResult } from "@/components/market/sale-result";
import { SellForm } from "@/components/market/sell-form";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import type { SquadMember } from "@/types/clubs.types";
import type { Sale } from "@/types/market.types";

type SellPlayerDialogProps = {
  member: SquadMember;
  clubName: string;
  isStarter: boolean;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function SellPlayerDialog({
  member,
  clubName,
  isStarter,
  open,
  onOpenChange,
}: SellPlayerDialogProps) {
  const router = useRouter();
  const [sale, setSale] = useState<Sale | null>(null);

  function handleOpenChange(next: boolean) {
    if (!next) {
      if (sale) router.refresh();
      setSale(null);
    }
    onOpenChange(next);
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[90svh] overflow-y-auto">
        {sale ? (
          <SaleResult
            sale={sale}
            member={member}
            clubName={clubName}
            wasStarter={isStarter}
            onClose={() => handleOpenChange(false)}
          />
        ) : (
          <SellForm
            member={member}
            clubName={clubName}
            isStarter={isStarter}
            onSold={setSale}
            onClose={() => handleOpenChange(false)}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}

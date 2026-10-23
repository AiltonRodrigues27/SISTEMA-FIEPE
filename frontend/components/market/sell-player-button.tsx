"use client";

import { HandCoins } from "lucide-react";
import { useState } from "react";
import { SellPlayerDialog } from "@/components/market/sell-player-dialog";
import { Button } from "@/components/ui/button";
import type { SquadMember } from "@/types/clubs.types";

type SellPlayerButtonProps = {
  member: SquadMember;
  clubName: string;
  isStarter: boolean;
};

export function SellPlayerButton({
  member,
  clubName,
  isStarter,
}: SellPlayerButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setIsOpen(true)}>
        <HandCoins aria-hidden />
        Vender
      </Button>
      <SellPlayerDialog
        member={member}
        clubName={clubName}
        isStarter={isStarter}
        open={isOpen}
        onOpenChange={setIsOpen}
      />
    </>
  );
}

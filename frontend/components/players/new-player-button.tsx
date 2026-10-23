"use client";

import { Plus } from "lucide-react";
import { useState } from "react";
import { PlayerFormDialog } from "@/components/players/player-form-dialog";
import { Button } from "@/components/ui/button";

type NewPlayerButtonProps = {
  variant?: "default" | "outline";
};

export function NewPlayerButton({ variant = "default" }: NewPlayerButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button variant={variant} onClick={() => setIsOpen(true)}>
        <Plus aria-hidden />
        Novo jogador
      </Button>
      <PlayerFormDialog open={isOpen} onOpenChange={setIsOpen} />
    </>
  );
}

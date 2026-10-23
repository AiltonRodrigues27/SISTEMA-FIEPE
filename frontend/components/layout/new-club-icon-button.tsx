"use client";

import { Plus } from "lucide-react";
import { useState } from "react";
import { NewClubDialog } from "@/components/clubs/new-club-dialog";
import { Button } from "@/components/ui/button";

export function NewClubIconButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button
        variant="ghost"
        size="icon-sm"
        aria-label="Novo clube"
        onClick={() => setIsOpen(true)}
      >
        <Plus aria-hidden />
      </Button>
      <NewClubDialog open={isOpen} onOpenChange={setIsOpen} />
    </>
  );
}

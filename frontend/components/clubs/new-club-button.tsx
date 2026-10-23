"use client";

import { Plus } from "lucide-react";
import { useState } from "react";
import { NewClubDialog } from "@/components/clubs/new-club-dialog";
import { Button } from "@/components/ui/button";

type NewClubButtonProps = {
  variant?: "default" | "outline";
};

export function NewClubButton({ variant = "default" }: NewClubButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button variant={variant} onClick={() => setIsOpen(true)}>
        <Plus aria-hidden />
        Novo clube
      </Button>
      <NewClubDialog open={isOpen} onOpenChange={setIsOpen} />
    </>
  );
}

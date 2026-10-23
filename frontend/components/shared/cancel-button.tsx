"use client";

import { useFormStatus } from "react-dom";
import { Button } from "@/components/ui/button";

export function CancelButton({ onClick }: { onClick: () => void }) {
  const { pending } = useFormStatus();

  return (
    <Button
      type="button"
      variant="outline"
      disabled={pending}
      onClick={onClick}
    >
      Cancelar
    </Button>
  );
}

"use client";

import { Download } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import type { TransactionType } from "@/types/market.types";

const TYPE_LABELS: Record<TransactionType, string> = {
  COMPRA: "Compra",
  VENDA: "Venda",
};

type ExportCsvButtonProps = {
  href: string;
  clubId: number;
  type?: TransactionType;
};

export function ExportCsvButton({ href, clubId, type }: ExportCsvButtonProps) {
  function announceDownload() {
    const filter = type
      ? `, com o filtro de tipo ${TYPE_LABELS[type]} aplicado`
      : "";

    toast.success("CSV baixado", {
      description: `transacoes-clube-${clubId}.csv${filter}.`,
    });
  }

  return (
    <Button
      variant="outline"
      nativeButton={false}
      render={<a href={href} download />}
      onClick={announceDownload}
    >
      <Download aria-hidden />
      Exportar CSV
    </Button>
  );
}

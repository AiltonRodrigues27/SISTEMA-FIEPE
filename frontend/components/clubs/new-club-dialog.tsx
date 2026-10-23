"use client";

import { Shield, Wallet } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { createClubAction } from "@/actions/clubs.actions";
import { AlertBanner } from "@/components/shared/alert-banner";
import { FormField } from "@/components/shared/form-field";
import { SubmitButton } from "@/components/shared/submit-button";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { formatMoney } from "@/utils/format";

function NewClubForm({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [acronym, setAcronym] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [refusedMessage, setRefusedMessage] = useState<string | null>(null);

  async function handleSubmit(formData: FormData) {
    const result = await createClubAction(formData);

    if (result.ok) {
      const { id, name: clubName, acronym: clubAcronym, cash } = result.data;
      toast.success(result.message, {
        description: `${clubName} (${clubAcronym}) começa com ${formatMoney(cash)} em caixa.`,
      });
      onClose();
      router.push(`/clubs/${id}`);
      return;
    }

    setFieldErrors(result.fieldErrors ?? {});
    setRefusedMessage(result.fieldErrors ? null : result.message);
    toast.error(result.message);
  }

  return (
    <form action={handleSubmit} className="grid gap-4">
      {refusedMessage && (
        <AlertBanner variant="danger" title="Não foi possível criar o clube">
          {refusedMessage}
        </AlertBanner>
      )}
      <FormField
        id="club-name"
        label="Nome"
        error={fieldErrors.name}
        hint="De 3 a 60 caracteres e de 2 a 5 palavras; só letras, espaços, hífen e ponto. Não pode repetir outro clube."
      >
        <div className="relative">
          <Shield
            className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            id="club-name"
            name="name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={60}
            placeholder="Ex.: Águias Futebol Clube"
            className="pl-9"
            aria-invalid={fieldErrors.name ? true : undefined}
            aria-describedby="club-name-message"
          />
        </div>
      </FormField>
      <FormField
        id="club-acronym"
        label="Sigla"
        error={fieldErrors.acronym}
        hint="3 letras de A a Z, maiúsculas, que aparecem no nome nessa ordem; a primeira é a primeira letra do nome."
      >
        <Input
          id="club-acronym"
          name="acronym"
          value={acronym}
          onChange={(event) => setAcronym(event.target.value.toUpperCase())}
          maxLength={3}
          placeholder="Ex.: AFC"
          aria-invalid={fieldErrors.acronym ? true : undefined}
          aria-describedby="club-acronym-message"
        />
      </FormField>
      <p className="flex items-center gap-2 rounded-lg border bg-muted-subtle p-3 text-body-sm text-muted-foreground">
        <Wallet className="size-4 shrink-0" aria-hidden />O clube começa com
        300,00 em caixa e sem jogadores.
      </p>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <SubmitButton pendingLabel="Criando…">Criar clube</SubmitButton>
      </DialogFooter>
    </form>
  );
}

type NewClubDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function NewClubDialog({ open, onOpenChange }: NewClubDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Novo clube</DialogTitle>
          <DialogDescription>
            Informe o nome e a sigla do clube.
          </DialogDescription>
        </DialogHeader>
        <NewClubForm onClose={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}

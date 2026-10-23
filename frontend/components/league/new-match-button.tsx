"use client";

import { Info, Plus, Shield, Swords } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { playMatchAction } from "@/actions/matches.actions";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ClubOption } from "@/types/clubs.types";

type ClubSelectProps = {
  name: string;
  label: string;
  hint: string;
  items: { value: string; label: string }[];
  value: string | null;
  onChange: (value: string | null) => void;
  error?: string;
};

function ClubSelect({
  name,
  label,
  hint,
  items,
  value,
  onChange,
  error,
}: ClubSelectProps) {
  return (
    <FormField id={name} label={label} hint={hint} error={error}>
      <Select name={name} items={items} value={value} onValueChange={onChange}>
        <SelectTrigger
          id={name}
          className="h-9 w-full"
          aria-invalid={error ? true : undefined}
        >
          <Shield className="text-muted-foreground" aria-hidden />
          <SelectValue placeholder="Escolha o clube" />
        </SelectTrigger>
        <SelectContent>
          {items.map((item) => (
            <SelectItem key={item.value} value={item.value}>
              {item.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </FormField>
  );
}

function NewMatchForm({
  clubs,
  onClose,
}: {
  clubs: ClubOption[];
  onClose: () => void;
}) {
  const router = useRouter();
  const [homeId, setHomeId] = useState<string | null>(null);
  const [awayId, setAwayId] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [refusedMessage, setRefusedMessage] = useState<string | null>(null);
  const items = clubs.map((club) => ({
    value: String(club.id),
    label: `${club.name} (${club.acronym})`,
  }));

  async function handleSubmit(formData: FormData) {
    const result = await playMatchAction(formData);

    if (result.ok) {
      const { matchId, home, away } = result.data;
      toast.success(result.message, {
        description: `${home.club_name} ${home.goals} × ${away.goals} ${away.club_name}. Placar e duelos devolvidos pela API.`,
      });
      onClose();
      router.push(`/matches/${matchId}`);
      return;
    }

    setFieldErrors(result.fieldErrors ?? {});
    setRefusedMessage(result.fieldErrors ? null : result.message);
  }

  return (
    <form action={handleSubmit} className="grid gap-4">
      {refusedMessage && (
        <AlertBanner variant="danger" title="Não foi possível jogar a partida">
          {refusedMessage}
        </AlertBanner>
      )}
      <ClubSelect
        name="home_club_id"
        label="Mandante"
        hint="Faz os 3 primeiros ataques."
        items={items}
        value={homeId}
        onChange={setHomeId}
        error={fieldErrors.home_club_id}
      />
      <ClubSelect
        name="away_club_id"
        label="Visitante"
        hint="Precisa ser um clube diferente do mandante."
        items={items}
        value={awayId}
        onChange={setAwayId}
        error={fieldErrors.away_club_id}
      />
      <div className="flex flex-col gap-1.5 rounded-lg border bg-muted-subtle p-3 text-caption text-muted-foreground">
        <p className="flex items-center gap-2 font-medium text-foreground">
          <Info className="size-3.5 shrink-0" aria-hidden />
          Como sai o placar
        </p>
        <p>
          Cada time faz 3 ataques. Pela ordem do elenco, os jogadores de linha
          vão do 1º (o mais recuado) ao 4º (o mais avançado): o 4º enfrenta o
          goleiro, o 3º enfrenta o 1º e o 2º enfrenta o 2º do adversário. O
          atacante usa finalização (ATA), passe (MEI) ou drible (ZAG e LAT), e
          quem defende usa defesa. É gol quando o ataque é maior; mal
          condicionado joga com 15% a menos.
        </p>
        <p>
          Os dois clubes precisam ter os 5 titulares escalados. A partida não
          mexe no caixa.
        </p>
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <SubmitButton pendingLabel="Jogando…">
          <Swords aria-hidden />
          Jogar partida
        </SubmitButton>
      </DialogFooter>
    </form>
  );
}

type NewMatchButtonProps = {
  clubs: ClubOption[];
  variant?: "default" | "outline";
};

export function NewMatchButton({
  clubs,
  variant = "default",
}: NewMatchButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button variant={variant} onClick={() => setIsOpen(true)}>
        <Plus aria-hidden />
        Nova partida
      </Button>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-h-[90svh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Nova partida</DialogTitle>
            <DialogDescription>
              Escolha o mandante e o visitante. O placar sai dos atributos dos
              titulares, sem sorteio.
            </DialogDescription>
          </DialogHeader>
          <NewMatchForm clubs={clubs} onClose={() => setIsOpen(false)} />
        </DialogContent>
      </Dialog>
    </>
  );
}

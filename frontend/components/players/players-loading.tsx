import {
  ChevronDown,
  Coins,
  HeartPulse,
  Search,
  Shield,
  Shirt,
  User,
} from "lucide-react";
import { ListLoading } from "@/components/shared/list-loading";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

const FILTERS = [
  { label: "Posição", icon: Shirt },
  { label: "Condição", icon: HeartPulse },
  { label: "Clube", icon: Shield },
  { label: "Idade", icon: User },
  { label: "Valor de mercado", icon: Coins },
];

const COLUMNS = [
  "Jogador",
  "Posição",
  "Overall",
  "Agilidade",
  "Idade",
  "Condição",
  "Valor base",
  "Valor de mercado",
  "Clube",
];

export function PlayersLoading() {
  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-52 flex-1">
          <Search
            className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            disabled
            placeholder="Buscar por nome"
            aria-label="Buscar jogador pelo nome"
            className="pl-9"
          />
        </div>
        {FILTERS.map(({ label, icon: Icon }) => (
          <Button
            key={label}
            variant="outline"
            disabled
            className="h-9 gap-2 font-normal"
          >
            <Icon className="text-muted-foreground" aria-hidden />
            {label}
            <ChevronDown className="text-muted-foreground" aria-hidden />
          </Button>
        ))}
      </div>
      <ListLoading
        label="Carregando jogadores…"
        columns={COLUMNS}
        rows={10}
        toolbar={<Skeleton className="h-9 w-44" />}
      />
    </>
  );
}

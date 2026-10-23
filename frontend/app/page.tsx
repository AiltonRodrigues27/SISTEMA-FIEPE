import {
  Clock,
  HandCoins,
  History,
  Shield,
  ShoppingCart,
  Trophy,
  Users,
} from "lucide-react";
import Image from "next/image";
import { Suspense } from "react";
import { FieldDecoration } from "@/components/league/field-decoration";
import { LeagueBadge } from "@/components/league/league-badge";
import { LeagueNumbers } from "@/components/league/league-numbers";
import { StartAction } from "@/components/league/start-action";
import { StepCard } from "@/components/league/step-card";
import { Skeleton } from "@/components/ui/skeleton";

const steps = [
  {
    icon: Users,
    title: "Jogadores",
    description:
      "Nascem livres e Apto; o valor de mercado vem da condição, agilidade e idade.",
  },
  {
    icon: Shield,
    title: "Clubes",
    description: "Começam com 300,00 em caixa e sem jogadores.",
  },
  {
    icon: ShoppingCart,
    title: "Compra",
    description: "Valor + taxa, até 50% do caixa, com contrato de fidelidade.",
  },
  {
    icon: HandCoins,
    title: "Venda",
    description: "Multa antes do fim da fidelidade e comissão sobre o lucro.",
  },
  {
    icon: History,
    title: "Histórico",
    description: "Toda compra e venda fica registrada, com totais e CSV.",
  },
  {
    icon: Trophy,
    title: "Liga",
    description:
      "Escale 5 titulares e jogue partidas que entram na classificação.",
  },
];

export default function HomePage() {
  return (
    <main className="relative flex min-h-svh items-center justify-center overflow-x-clip px-4 py-8 xl:h-svh xl:overflow-hidden xl:p-0">
      {/* Em xl o palco é o quadro do Figma (1440 × 900) reduzido para caber na
          janela; a referência 1320 × 820 tira a margem branca e cresce o conteúdo. */}
      <div className="relative flex w-full flex-col items-center gap-8 xl:h-225 xl:w-360 xl:shrink-0 xl:scale-[min(1,tan(atan2(100svh,820px)),tan(atan2(100vw,1320px)))] xl:justify-center">
        <FieldDecoration />
        <section className="relative flex w-full max-w-180 flex-col items-center gap-5.5 rounded-3xl bg-background px-6 py-8 xl:px-12">
          <div className="flex items-center gap-5">
            <Image src="/passe-mark.svg" alt="" width={56} height={56} />
            <span className="text-[32px] leading-10 font-semibold tracking-[-0.03em]">
              Passe
            </span>
          </div>
          <Suspense fallback={<Skeleton className="h-6.5 w-64 rounded-full" />}>
            <LeagueBadge />
          </Suspense>
          <div className="flex w-full flex-col items-center gap-3 text-center">
            <h1 className="text-[28px] leading-9 font-semibold tracking-tight text-balance md:text-[40px] md:leading-12 md:whitespace-nowrap">
              Gestão da liga, do mercado à classificação
            </h1>
            <p className="text-body text-muted-foreground">
              Cadastre jogadores, monte os clubes e negocie com contrato de
              fidelidade. Depois, escale os titulares e jogue partidas com
              placar calculado pelos atributos.
            </p>
          </div>
          <StartAction />
          <Suspense fallback={<Skeleton className="h-4 w-80 max-w-full" />}>
            <LeagueNumbers />
          </Suspense>
        </section>
        <ol className="relative grid w-full max-w-180 grid-cols-1 gap-2 sm:grid-cols-2 md:grid-cols-3 xl:flex xl:max-w-none xl:items-center xl:justify-center">
          {steps.map((step, index) => (
            <StepCard
              key={step.title}
              number={String(index + 1).padStart(2, "0")}
              icon={step.icon}
              title={step.title}
              description={step.description}
              hasNext={index < steps.length - 1}
            />
          ))}
        </ol>
        <p className="relative flex items-center gap-1.5 text-caption text-muted-foreground">
          <Clock className="size-4" aria-hidden />
          Liga Fictícia 2026 · Horário de Brasília (UTC−3)
        </p>
      </div>
    </main>
  );
}

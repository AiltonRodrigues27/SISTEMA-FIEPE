"use client";

import { ChevronDown, type LucideIcon } from "lucide-react";
import { useState } from "react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import type { RangeLimits } from "@/types/filters.types";

function validateRange(
  minText: string,
  maxText: string,
  limits: RangeLimits,
): string | null {
  const texts = [minText, maxText].filter((text) => text !== "");
  const invalid = texts.some((text) => {
    const number = Number(text);
    return (
      Number.isNaN(number) ||
      number < limits.min ||
      number > limits.max ||
      (limits.integer
        ? !Number.isInteger(number)
        : Math.round(number * 100) / 100 !== number)
    );
  });

  if (invalid) {
    return limits.integer
      ? `Use números inteiros de ${limits.min} a ${limits.max}.`
      : `Use valores de ${limits.min} a ${limits.max}, com até 2 casas.`;
  }
  if (texts.length === 2 && Number(minText) > Number(maxText)) {
    return "O mínimo não pode ser maior que o máximo.";
  }
  return null;
}

type RangeFilterProps = {
  icon: LucideIcon;
  label: string;
  activeLabel: string;
  activeText: string | null;
  limits: RangeLimits;
  minKey: string;
  maxKey: string;
  minValue: string;
  maxValue: string;
  onApply: (changes: Record<string, string | null>) => void;
};

export function RangeFilter({
  icon: Icon,
  label,
  activeLabel,
  activeText,
  limits,
  minKey,
  maxKey,
  minValue,
  maxValue,
  onApply,
}: RangeFilterProps) {
  const [open, setOpen] = useState(false);
  const [minText, setMinText] = useState(minValue);
  const [maxText, setMaxText] = useState(maxValue);
  const [error, setError] = useState<string | null>(null);

  function apply() {
    const message = validateRange(minText, maxText, limits);
    setError(message);
    if (message) return;

    onApply({ [minKey]: minText || null, [maxKey]: maxText || null });
    setOpen(false);
  }

  function clear() {
    setMinText("");
    setMaxText("");
    setError(null);
    onApply({ [minKey]: null, [maxKey]: null });
    setOpen(false);
  }

  return (
    <Popover
      open={open}
      onOpenChange={(next) => {
        if (next) {
          setMinText(minValue);
          setMaxText(maxValue);
          setError(null);
        }
        setOpen(next);
      }}
    >
      <PopoverTrigger
        className={cn(
          buttonVariants({ variant: "outline" }),
          "h-9 shrink-0 justify-start gap-2 border-input px-3 font-normal shadow-xs",
        )}
      >
        <Icon className="text-muted-foreground" aria-hidden />
        {activeText ? `${activeLabel}: ${activeText}` : label}
        <ChevronDown className="text-muted-foreground" aria-hidden />
      </PopoverTrigger>
      <PopoverContent className="w-64 gap-3 rounded-lg p-3">
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor={minKey}>Mínimo</Label>
            <Input
              id={minKey}
              type="number"
              inputMode="decimal"
              step={limits.integer ? 1 : 0.01}
              value={minText}
              onChange={(event) => setMinText(event.target.value)}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor={maxKey}>Máximo</Label>
            <Input
              id={maxKey}
              type="number"
              inputMode="decimal"
              step={limits.integer ? 1 : 0.01}
              value={maxText}
              onChange={(event) => setMaxText(event.target.value)}
            />
          </div>
        </div>
        {error && (
          <p role="alert" className="text-caption text-destructive">
            {error}
          </p>
        )}
        <div className="flex justify-end gap-2">
          <Button variant="ghost" size="sm" onClick={clear}>
            Limpar
          </Button>
          <Button size="sm" onClick={apply}>
            Aplicar
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}

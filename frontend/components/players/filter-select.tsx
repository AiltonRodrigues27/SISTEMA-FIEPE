"use client";

import type { LucideIcon } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

const ALL = "all";

type FilterSelectProps = {
  icon: LucideIcon;
  placeholder: string;
  allLabel: string;
  value: string | null;
  options: { value: string; label: string }[];
  disabled?: boolean;
  className?: string;
  onChange: (value: string | null) => void;
};

export function FilterSelect({
  icon: Icon,
  placeholder,
  allLabel,
  value,
  options,
  disabled,
  className,
  onChange,
}: FilterSelectProps) {
  const items = [{ value: ALL, label: allLabel }, ...options];

  return (
    <Select
      items={items}
      value={value}
      disabled={disabled}
      onValueChange={(next) => onChange(next === ALL ? null : next)}
    >
      <SelectTrigger
        aria-label={placeholder}
        className={cn(
          "h-9 shrink-0",
          disabled && "pointer-events-none",
          className,
        )}
      >
        <Icon className="text-muted-foreground" aria-hidden />
        {value && <span>{placeholder}:</span>}
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {items.map((item) => (
          <SelectItem key={item.value} value={item.value}>
            {item.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

import { Badge } from "@/components/ui/badge";
import type { PlayerCondition } from "@/types/players.types";
import { CONDITION_LABELS } from "@/utils/labels";

const VARIANTS = {
  APTO: "success",
  MAL_CONDICIONADO: "warning",
  DOENTE: "danger",
} as const;

export function ConditionBadge({ condition }: { condition: PlayerCondition }) {
  return (
    <Badge variant={VARIANTS[condition]}>
      <span aria-hidden className="size-1.5 rounded-full bg-current" />
      {CONDITION_LABELS[condition]}
    </Badge>
  );
}

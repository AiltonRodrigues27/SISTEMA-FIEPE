import { Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function PenaltyBadge({ rate }: { rate: number }) {
  if (rate === 0) {
    return (
      <Badge variant="success">
        <Check aria-hidden />
        0%
      </Badge>
    );
  }
  return <Badge variant="warning">{rate}%</Badge>;
}

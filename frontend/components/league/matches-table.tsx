import { ChevronRight } from "lucide-react";
import Link from "next/link";
import {
  TABLE_CELL_CLASS as CELL,
  TABLE_HEAD_CLASS as HEAD,
} from "@/components/shared/table-classes";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { MatchSummary } from "@/types/matches.types";
import { formatDate, formatTime } from "@/utils/format";
import { MATCH_RESULT_LABELS } from "@/utils/labels";

type MatchesTableProps = {
  matches: MatchSummary[];
  acronyms: Map<number, string>;
};

export function MatchesTable({ matches, acronyms }: MatchesTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
          <TableHead className={cn(HEAD, "whitespace-nowrap")}>
            Data e hora
          </TableHead>
          <TableHead className={cn(HEAD, "min-w-40 text-right")}>
            Mandante
          </TableHead>
          <TableHead className={cn(HEAD, "text-center")}>Placar</TableHead>
          <TableHead className={cn(HEAD, "min-w-40")}>Visitante</TableHead>
          <TableHead className={HEAD}>Resultado</TableHead>
          <TableHead className={HEAD}>
            <span className="sr-only">Duelos</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {matches.map((match) => (
          <TableRow key={match.id} className="h-12">
            <TableCell className={cn(CELL, "text-body-sm whitespace-nowrap")}>
              {formatDate(match.played_at)}{" "}
              <span className="text-muted-foreground">
                {formatTime(match.played_at)}
              </span>
            </TableCell>
            <TableCell className={cn(CELL, "text-right")}>
              <span className="inline-flex items-center gap-2">
                <span className="text-body-sm font-semibold">
                  {match.home.club_name}
                </span>
                <Badge variant="outline">
                  {acronyms.get(match.home.club_id) ?? "—"}
                </Badge>
              </span>
            </TableCell>
            <TableCell
              className={cn(
                CELL,
                "text-center text-body-sm font-semibold whitespace-nowrap tabular-nums",
              )}
            >
              {match.home.goals} × {match.away.goals}
            </TableCell>
            <TableCell className={CELL}>
              <span className="inline-flex items-center gap-2">
                <Badge variant="outline">
                  {acronyms.get(match.away.club_id) ?? "—"}
                </Badge>
                <span className="text-body-sm font-semibold">
                  {match.away.club_name}
                </span>
              </span>
            </TableCell>
            <TableCell className={CELL}>
              <Badge variant="outline">
                {MATCH_RESULT_LABELS[match.result]}
              </Badge>
            </TableCell>
            <TableCell className={cn(CELL, "text-right")}>
              <Link
                href={`/matches/${match.id}`}
                className="inline-flex items-center gap-1 text-body-sm font-medium whitespace-nowrap hover:underline"
              >
                Ver duelos
                <ChevronRight className="size-4" aria-hidden />
              </Link>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

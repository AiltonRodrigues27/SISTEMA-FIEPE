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
import type { StandingRow } from "@/types/standings.types";
import { formatSignedInteger } from "@/utils/format";

const NUMBER_HEAD = cn(HEAD, "text-right");
const NUMBER_CELL = cn(CELL, "text-right text-body-sm tabular-nums");

type StandingsTableProps = {
  rows: StandingRow[];
  acronyms: Map<number, string>;
};

export function StandingsTable({ rows, acronyms }: StandingsTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
          <TableHead className={cn(HEAD, "w-12")}>#</TableHead>
          <TableHead className={cn(HEAD, "min-w-44")}>Clube</TableHead>
          <TableHead className={NUMBER_HEAD}>J</TableHead>
          <TableHead className={NUMBER_HEAD}>V</TableHead>
          <TableHead className={NUMBER_HEAD}>E</TableHead>
          <TableHead className={NUMBER_HEAD}>D</TableHead>
          <TableHead className={NUMBER_HEAD}>GP</TableHead>
          <TableHead className={NUMBER_HEAD}>GC</TableHead>
          <TableHead className={NUMBER_HEAD}>SG</TableHead>
          <TableHead className={NUMBER_HEAD}>Pts</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row) => (
          <TableRow key={row.club_id} className="h-12">
            <TableCell className={CELL}>
              <span
                className={cn(
                  "flex size-6 items-center justify-center rounded-md text-caption font-medium",
                  row.position === 1
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground",
                )}
              >
                {row.position}
              </span>
            </TableCell>
            <TableCell className={CELL}>
              <span className="inline-flex items-center gap-2">
                <Badge variant="outline">
                  {acronyms.get(row.club_id) ?? "—"}
                </Badge>
                <Link
                  href={`/clubs/${row.club_id}`}
                  className="text-body-sm font-medium underline underline-offset-2"
                >
                  {row.club_name}
                </Link>
              </span>
            </TableCell>
            <TableCell className={NUMBER_CELL}>{row.played}</TableCell>
            <TableCell className={NUMBER_CELL}>{row.wins}</TableCell>
            <TableCell className={NUMBER_CELL}>{row.draws}</TableCell>
            <TableCell className={NUMBER_CELL}>{row.losses}</TableCell>
            <TableCell className={NUMBER_CELL}>{row.goals_for}</TableCell>
            <TableCell className={NUMBER_CELL}>{row.goals_against}</TableCell>
            <TableCell className={NUMBER_CELL}>
              {formatSignedInteger(row.goal_difference)}
            </TableCell>
            <TableCell className={cn(NUMBER_CELL, "font-semibold")}>
              {row.points}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

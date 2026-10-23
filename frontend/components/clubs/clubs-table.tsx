import { ChevronRight } from "lucide-react";
import Link from "next/link";
import {
  TABLE_CELL_CLASS as CELL,
  TABLE_HEAD_CLASS as HEAD,
} from "@/components/shared/table-classes";
import { ClubTile } from "@/components/shared/club-tile";
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
import type { Club } from "@/types/clubs.types";
import { formatMoney } from "@/utils/format";

export function ClubsTable({ clubs }: { clubs: Club[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
          <TableHead className={cn(HEAD, "min-w-48")}>Clube</TableHead>
          <TableHead className={HEAD}>Sigla</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Caixa</TableHead>
          <TableHead className={cn(HEAD, "text-right")}>
            Valor do elenco
          </TableHead>
          <TableHead className={cn(HEAD, "text-right")}>Patrimônio</TableHead>
          <TableHead className={HEAD}>
            <span className="sr-only">Ações</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {clubs.map((club) => (
          <TableRow key={club.id} className="h-14">
            <TableCell className={CELL}>
              <div className="flex items-center gap-3">
                <ClubTile acronym={club.acronym} />
                <span className="text-body-sm font-medium">{club.name}</span>
              </div>
            </TableCell>
            <TableCell className={CELL}>
              <Badge variant="outline">{club.acronym}</Badge>
            </TableCell>
            <TableCell className={cn(CELL, "text-right text-body-sm")}>
              {formatMoney(club.cash)}
            </TableCell>
            <TableCell className={cn(CELL, "text-right text-body-sm")}>
              {formatMoney(club.squad_value)}
            </TableCell>
            <TableCell
              className={cn(CELL, "text-right text-body-sm font-semibold")}
            >
              {formatMoney(club.net_worth)}
            </TableCell>
            <TableCell className={cn(CELL, "text-right")}>
              <Link
                href={`/clubs/${club.id}`}
                className="inline-flex items-center gap-1 text-body-sm font-medium whitespace-nowrap hover:underline"
              >
                Ver clube
                <span className="sr-only">{club.name}</span>
                <ChevronRight className="size-4" aria-hidden />
              </Link>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

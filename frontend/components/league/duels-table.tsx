import { PlayerAvatar } from "@/components/players/player-avatar";
import { ClubTile } from "@/components/shared/club-tile";
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
import type { Duel, DuelPlayer, MatchDetail } from "@/types/matches.types";
import { pluralize } from "@/utils/format";
import { ATTRIBUTE_LABELS } from "@/utils/labels";

const ATTACKER_LINES = [4, 3, 2];
const DEFENDER_LINES = [null, 1, 2];

function describePlayer(
  player: DuelPlayer,
  line: number | null,
  clubName: string,
): string {
  return line === null
    ? `Goleiro · ${clubName}`
    : `${player.position} · ${line}º de linha · ${clubName}`;
}

function PlayerCell({
  player,
  description,
}: {
  player: DuelPlayer;
  description: string;
}) {
  return (
    <div className="flex items-center gap-3">
      <PlayerAvatar id={player.player_id} name={player.player_name} />
      <div className="flex min-w-0 flex-col">
        <span className="text-body-sm font-medium">{player.player_name}</span>
        <span className="text-caption whitespace-nowrap text-muted-foreground">
          {description}
        </span>
      </div>
    </div>
  );
}

function ValueCell({ player }: { player: DuelPlayer }) {
  return (
    <span className="text-body-sm whitespace-nowrap">
      <span className="text-muted-foreground">
        {ATTRIBUTE_LABELS[player.attribute] ?? player.attribute}
      </span>{" "}
      <span className="font-semibold tabular-nums">{player.value}</span>
    </span>
  );
}

type AttackGroupProps = {
  title: string;
  acronym: string;
  goals: number;
  duels: Duel[];
  attackerClub: string;
  defenderClub: string;
};

function AttackGroup({
  title,
  acronym,
  goals,
  duels,
  attackerClub,
  defenderClub,
}: AttackGroupProps) {
  return (
    <>
      <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
        <TableCell colSpan={6} className={CELL}>
          <div className="flex items-center justify-between gap-3">
            <span className="flex items-center gap-2 text-body-sm font-medium">
              <ClubTile acronym={acronym} className="h-6 min-w-9" />
              {title}
            </span>
            <span className="text-caption text-muted-foreground">
              {goals} {pluralize(goals, "gol", "gols")}
            </span>
          </div>
        </TableCell>
      </TableRow>
      {duels.map((duel, index) => (
        <TableRow key={duel.order} className="h-14">
          <TableCell className={cn(CELL, "text-body-sm tabular-nums")}>
            {duel.order}
          </TableCell>
          <TableCell className={CELL}>
            <PlayerCell
              player={duel.attacker}
              description={describePlayer(
                duel.attacker,
                ATTACKER_LINES[index],
                attackerClub,
              )}
            />
          </TableCell>
          <TableCell className={CELL}>
            <ValueCell player={duel.attacker} />
          </TableCell>
          <TableCell className={CELL}>
            <PlayerCell
              player={duel.defender}
              description={describePlayer(
                duel.defender,
                DEFENDER_LINES[index],
                defenderClub,
              )}
            />
          </TableCell>
          <TableCell className={CELL}>
            <ValueCell player={duel.defender} />
          </TableCell>
          <TableCell className={cn(CELL, "text-right")}>
            <Badge variant={duel.goal ? "success" : "outline"}>
              {duel.goal ? "Gol" : "Sem gol"}
            </Badge>
          </TableCell>
        </TableRow>
      ))}
    </>
  );
}

type DuelsTableProps = {
  match: MatchDetail;
  acronyms: Map<number, string>;
};

export function DuelsTable({ match, acronyms }: DuelsTableProps) {
  const { home, away } = match;
  const duelsOf = (clubId: number) =>
    match.duels
      .filter((duel) => duel.attacking_club_id === clubId)
      .sort((a, b) => a.order - b.order);

  return (
    <section className="overflow-hidden rounded-xl border bg-card shadow-xs">
      <div className="flex flex-col gap-1 p-4">
        <h2 className="text-heading-card">Duelos</h2>
        <p className="text-caption text-muted-foreground">
          Os 3 ataques do mandante e depois os 3 do visitante. Os jogadores de
          linha vão do 1º (o mais recuado) ao 4º (o mais avançado), pela ordem
          do elenco: o 4º ataca o goleiro, o 3º ataca o 1º e o 2º ataca o 2º.
        </p>
      </div>
      <Table>
        <TableHeader>
          <TableRow className="bg-muted-subtle hover:bg-muted-subtle">
            <TableHead className={cn(HEAD, "w-16")}>Duelo</TableHead>
            <TableHead className={cn(HEAD, "min-w-52")}>Atacante</TableHead>
            <TableHead className={HEAD}>Ataque</TableHead>
            <TableHead className={cn(HEAD, "min-w-52")}>Defensor</TableHead>
            <TableHead className={HEAD}>Defesa</TableHead>
            <TableHead className={cn(HEAD, "text-right")}>Resultado</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <AttackGroup
            title={`Ataques do ${home.club_name} (mandante)`}
            acronym={acronyms.get(home.club_id) ?? "—"}
            goals={home.goals}
            duels={duelsOf(home.club_id)}
            attackerClub={home.club_name}
            defenderClub={away.club_name}
          />
          <AttackGroup
            title={`Ataques do ${away.club_name} (visitante)`}
            acronym={acronyms.get(away.club_id) ?? "—"}
            goals={away.goals}
            duels={duelsOf(away.club_id)}
            attackerClub={away.club_name}
            defenderClub={home.club_name}
          />
        </TableBody>
      </Table>
    </section>
  );
}

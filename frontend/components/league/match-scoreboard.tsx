import { ClubTile } from "@/components/shared/club-tile";
import { Badge } from "@/components/ui/badge";
import type { MatchSide, MatchSummary } from "@/types/matches.types";
import { formatDate, formatTime } from "@/utils/format";
import { MATCH_RESULT_LABELS } from "@/utils/labels";

type SideInfoProps = {
  side: MatchSide;
  role: string;
  withFormation: boolean;
  align: "left" | "right";
};

function SideInfo({ side, role, withFormation, align }: SideInfoProps) {
  return (
    <div
      className={`flex min-w-0 flex-col ${align === "right" ? "items-end text-right" : "items-start text-left"}`}
    >
      <span className="max-w-full truncate text-body-sm font-semibold">
        {side.club_name}
      </span>
      <span className="text-caption text-muted-foreground">
        {role}
        {withFormation ? ` · ${side.formation}` : ""}
      </span>
    </div>
  );
}

type MatchScoreboardProps = {
  match: MatchSummary;
  acronyms: Map<number, string>;
  withFormation?: boolean;
};

export function MatchScoreboard({
  match,
  acronyms,
  withFormation = false,
}: MatchScoreboardProps) {
  const { home, away } = match;

  return (
    <div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-3 sm:gap-5">
      <div className="flex items-center justify-end gap-3">
        <SideInfo
          side={home}
          role="Mandante"
          withFormation={withFormation}
          align="right"
        />
        <ClubTile
          acronym={acronyms.get(home.club_id) ?? "—"}
          className="h-10 min-w-11"
        />
      </div>
      <div className="flex flex-col items-center gap-1">
        <span className="text-heading-page tabular-nums">
          {home.goals} × {away.goals}
        </span>
        <span className="text-caption whitespace-nowrap text-muted-foreground">
          {formatDate(match.played_at)}, {formatTime(match.played_at)}
        </span>
        <Badge variant="outline">{MATCH_RESULT_LABELS[match.result]}</Badge>
      </div>
      <div className="flex items-center gap-3">
        <ClubTile
          acronym={acronyms.get(away.club_id) ?? "—"}
          className="h-10 min-w-11"
        />
        <SideInfo
          side={away}
          role="Visitante"
          withFormation={withFormation}
          align="left"
        />
      </div>
    </div>
  );
}

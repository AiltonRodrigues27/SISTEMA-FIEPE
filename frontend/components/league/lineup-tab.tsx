import { LineupEditor } from "@/components/league/lineup-editor";
import { ErrorState } from "@/components/shared/error-state";
import type { ApiResult } from "@/types/api.types";
import type { Lineup } from "@/types/league.types";
import type { Player } from "@/types/players.types";

type LineupTabProps = {
  clubId: number;
  clubName: string;
  squad: Player[];
  lineup: ApiResult<Lineup>;
};

export function LineupTab({ clubId, clubName, squad, lineup }: LineupTabProps) {
  if (!lineup.ok) {
    return (
      <section className="rounded-xl border bg-card shadow-xs">
        <ErrorState
          title="Não foi possível carregar a escalação"
          message={lineup.message}
        />
      </section>
    );
  }

  const savedLineupKey = `${lineup.data.formation}-${lineup.data.players.map((player) => player.id).join(",")}`;

  return (
    <LineupEditor
      key={savedLineupKey}
      clubId={clubId}
      clubName={clubName}
      squad={squad}
      lineup={lineup.data}
    />
  );
}

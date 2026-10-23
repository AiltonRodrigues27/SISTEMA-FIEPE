import Link from "next/link";
import { cn } from "@/lib/utils";
import type { MatchSummary } from "@/types/matches.types";
import { formatDate, formatTime } from "@/utils/format";

const TABLE_ORDER = [
  "Mais pontos",
  "Maior saldo de gols",
  "Mais gols marcados",
  "Nome do clube, de A a Z",
];

const RECENT_MATCHES_LIMIT = 3;

export function RecentMatchesCard({ matches }: { matches: MatchSummary[] }) {
  return (
    <section className="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-xs">
      <div className="flex flex-col gap-1">
        <h2 className="text-heading-card">Últimas partidas</h2>
        <p className="text-caption text-muted-foreground">
          Da mais recente à mais antiga.
        </p>
      </div>
      {matches.length === 0 ? (
        <p className="text-body-sm text-muted-foreground">
          Nenhuma partida jogada ainda.
        </p>
      ) : (
        <ul className="flex flex-col gap-3">
          {matches.slice(0, RECENT_MATCHES_LIMIT).map((match) => (
            <li key={match.id} className="flex flex-col">
              <span className="text-caption text-muted-foreground">
                {formatDate(match.played_at)}, {formatTime(match.played_at)}
              </span>
              <span className="text-body-sm">
                <span
                  className={cn(match.result === "MANDANTE" && "font-semibold")}
                >
                  {match.home.club_name}
                </span>{" "}
                <span className="font-semibold tabular-nums">
                  {match.home.goals} × {match.away.goals}
                </span>{" "}
                <span
                  className={cn(
                    match.result === "VISITANTE" && "font-semibold",
                  )}
                >
                  {match.away.club_name}
                </span>
              </span>
            </li>
          ))}
        </ul>
      )}
      <Link
        href="/matches"
        className="text-body-sm font-medium text-primary hover:underline"
      >
        Ver todas as partidas →
      </Link>
    </section>
  );
}

export function TableOrderCard() {
  return (
    <section className="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-xs">
      <div className="flex flex-col gap-1">
        <h2 className="text-heading-card">Ordem da tabela</h2>
        <p className="text-caption text-muted-foreground">
          Critério de classificação, nesta ordem.
        </p>
      </div>
      <ol className="flex flex-col gap-2">
        {TABLE_ORDER.map((criterion, index) => (
          <li
            key={criterion}
            className="flex items-center gap-2.5 text-body-sm"
          >
            <span
              aria-hidden
              className="flex size-5 shrink-0 items-center justify-center rounded-md bg-muted text-caption font-medium text-muted-foreground"
            >
              {index + 1}
            </span>
            {criterion}
          </li>
        ))}
      </ol>
    </section>
  );
}

import { History } from "lucide-react";
import { ExportCsvButton } from "@/components/market/export-csv-button";
import { TransactionsFilters } from "@/components/market/transactions-filters";
import { TransactionsSummary } from "@/components/market/transactions-summary";
import { TransactionsTable } from "@/components/market/transactions-table";
import { AlertBanner } from "@/components/shared/alert-banner";
import { EmptyState } from "@/components/shared/empty-state";
import { getClubTransactions } from "@/services/market.service";
import type {
  TransactionHistory,
  TransactionsQuery,
} from "@/types/market.types";
import { buildTransactionsExportUrl } from "@/utils/transactions-export-url";

type ClubHistoryProps = {
  clubId: number;
  filters: TransactionsQuery;
  history: TransactionHistory;
};

export async function ClubHistory({
  clubId,
  filters,
  history,
}: ClubHistoryProps) {
  const hasFilters =
    filters.type !== undefined || filters.player_id !== undefined;
  const filtered = hasFilters
    ? await getClubTransactions(clubId, filters)
    : { ok: true as const, data: history };

  const playersInHistory = [
    ...new Map(
      history.data.map((item) => [item.player_id, item.player_name]),
    ).entries(),
  ].map(([id, name]) => ({ id, name }));

  return (
    <>
      <div className="flex flex-col gap-4 p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex flex-col gap-1">
            <h2 className="text-heading-card">Histórico de transações</h2>
            <p className="text-caption text-muted-foreground">
              Da mais recente para a mais antiga, com o nome e os valores do
              momento de cada operação.
            </p>
          </div>
          <ExportCsvButton
            href={buildTransactionsExportUrl(clubId, filters)}
            clubId={clubId}
            type={filters.type}
          />
        </div>
        <TransactionsFilters
          clubId={clubId}
          filters={filters}
          players={playersInHistory}
        />
      </div>
      {!filtered.ok ? (
        <div className="px-4 pb-4">
          <AlertBanner variant="danger" title="O filtro foi recusado">
            {filtered.message}
          </AlertBanner>
        </div>
      ) : (
        <>
          {filtered.data.data.length === 0 ? (
            <EmptyState
              icon={History}
              title="Nenhuma transação ainda"
              description={
                hasFilters
                  ? "Nenhuma transação bate com os filtros escolhidos."
                  : "As compras e vendas do clube aparecem aqui, com os totais logo abaixo."
              }
            />
          ) : (
            <TransactionsTable transactions={filtered.data.data} />
          )}
          <TransactionsSummary summary={filtered.data.summary} />
        </>
      )}
    </>
  );
}

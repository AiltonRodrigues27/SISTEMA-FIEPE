export type TransactionType = "COMPRA" | "VENDA";

export type Transaction = {
  id: number;
  club_id: number;
  player_id: number;
  player_name: string;
  type: TransactionType;
  value: number;
  fee: number;
  penalty: number;
  profit: number | null;
  cash_change: number;
  created_at: string;
};

export type BuyPlayerBody = {
  club_id: number;
  loyalty_until: string;
};

export type Purchase = Transaction & {
  contract: {
    purchase_value: number;
    loyalty_until: string;
    status: string;
  };
  club_cash: number;
};

export type Sale = Transaction & {
  purchase_value: number;
  remaining_days: number;
  penalty_rate: number;
  contract_status: string;
  club_cash: number;
};

export type TransactionSummary = {
  total_spent: number;
  total_received: number;
  total_fees: number;
  total_penalties: number;
  total_profit: number;
};

export type TransactionHistory = {
  data: Transaction[];
  summary: TransactionSummary;
};

export type TransactionsQuery = {
  type?: TransactionType;
  player_id?: number;
};

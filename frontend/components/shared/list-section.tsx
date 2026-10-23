import type { ReactNode } from "react";
import { ErrorState } from "@/components/shared/error-state";
import { ListCard } from "@/components/shared/list-card";
import type { ApiResult } from "@/types/api.types";

type ListSectionProps<TData> = {
  result: ApiResult<TData>;
  errorTitle: string;
  errorHint?: string;
  isEmpty?: (data: TData) => boolean;
  empty?: ReactNode;
  children: (data: TData) => ReactNode;
};

export function ListSection<TData>({
  result,
  errorTitle,
  errorHint,
  isEmpty,
  empty,
  children,
}: ListSectionProps<TData>) {
  return (
    <ListCard>
      {!result.ok ? (
        <ErrorState
          title={errorTitle}
          message={result.message}
          hint={errorHint}
        />
      ) : isEmpty?.(result.data) ? (
        empty
      ) : (
        children(result.data)
      )}
    </ListCard>
  );
}

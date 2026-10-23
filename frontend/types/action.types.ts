type ActionFailure = {
  ok: false;
  message: string;
  fieldErrors?: Record<string, string>;
  isNetworkError?: boolean;
};

export type Refusal = {
  title: string;
  message: string;
  isNetworkError: boolean;
};

export type ActionResult ={ ok: true; message: string } | ActionFailure;

export type ActionResultWithData<TData> =
  { ok: true; message: string; data: TData } | ActionFailure;

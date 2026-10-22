export type ApiError = { status: number | null; message: string };

export type ApiResult<T> = { ok: true; data: T } | ({ ok: false } & ApiError);

type AttributeBarProps = {
  label: string;
  value: number | null;
  potential?: number;
};

export function AttributeBar({ label, value, potential }: AttributeBarProps) {
  return (
    <div className="flex items-center gap-3 text-body-sm">
      <span className="w-24 shrink-0 text-muted-foreground">{label}</span>
      <span
        aria-hidden
        className="relative h-2 flex-1 overflow-hidden rounded-full bg-muted"
      >
        {potential !== undefined && (
          <span
            className="absolute inset-y-0 left-0 rounded-full bg-primary/25"
            style={{ width: `${potential}%` }}
          />
        )}
        {value !== null && (
          <span
            className="absolute inset-y-0 left-0 rounded-full bg-primary"
            style={{ width: `${value}%` }}
          />
        )}
      </span>
      <span className="w-7 text-right font-medium tabular-nums">
        {value ?? "—"}
      </span>
    </div>
  );
}

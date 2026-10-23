import { Lock } from "lucide-react";

type LockedFieldProps = {
  label: string;
  hint: string;
};

export function LockedField({ label, hint }: LockedFieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-sm leading-none font-medium text-muted-foreground">
        {label}
      </span>
      <div className="flex h-9 items-center gap-2 rounded-md bg-muted px-3 text-body-sm text-muted-foreground">
        <Lock className="size-3.5" aria-hidden />
        Após salvar
      </div>
      <p className="text-caption text-muted-foreground">{hint}</p>
    </div>
  );
}

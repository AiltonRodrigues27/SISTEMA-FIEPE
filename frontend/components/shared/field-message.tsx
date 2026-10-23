import { CircleAlert } from "lucide-react";

type FieldMessageProps = {
  id: string;
  hint?: string;
  error?: string;
};

export function FieldMessage({ id, hint, error }: FieldMessageProps) {
  if (error) {
    return (
      <p
        id={id}
        role="alert"
        className="flex items-center gap-1 text-caption text-destructive"
      >
        <CircleAlert className="size-3.5 shrink-0" aria-hidden />
        {error}
      </p>
    );
  }
  if (hint) {
    return (
      <p id={id} className="text-caption text-muted-foreground">
        {hint}
      </p>
    );
  }
  return null;
}

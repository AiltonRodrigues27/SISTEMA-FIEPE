import { ImageOff } from "lucide-react";
import { RetryButton } from "@/components/shared/retry-button";

type ErrorStateProps = {
  title: string;
  message: string;
  hint?: string;
};

export function ErrorState({ title, message, hint }: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center gap-3 px-4 py-14 text-center"
    >
      <span className="flex size-12 items-center justify-center rounded-xl bg-muted text-muted-foreground">
        <ImageOff className="size-5" aria-hidden />
      </span>
      <div className="flex max-w-md flex-col gap-1">
        <p className="text-body-sm font-medium">{title}</p>
        <p className="text-body-sm text-muted-foreground">
          {message}
          {hint ? ` ${hint}` : ""}
        </p>
      </div>
      <RetryButton />
    </div>
  );
}

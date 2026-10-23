import type { ReactNode } from "react";
import { FieldMessage } from "@/components/shared/field-message";
import { Label } from "@/components/ui/label";

type FormFieldProps = {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  children: ReactNode;
};

export function FormField({
  id,
  label,
  hint,
  error,
  children,
}: FormFieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      {children}
      <FieldMessage id={`${id}-message`} hint={hint} error={error} />
    </div>
  );
}

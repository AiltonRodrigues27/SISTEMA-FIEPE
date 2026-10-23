import { cn } from "@/lib/utils";
import type { Formation } from "@/types/league.types";
import {
  FORMATIONS,
  FORMATION_SHAPES,
  describeFormation,
} from "@/utils/formations";

function FormationIcon({ formation }: { formation: Formation }) {
  const { defense, midfield, attack } = FORMATION_SHAPES[formation];
  const goalkeeper = 1;
  const rows = [attack, midfield, defense, goalkeeper].filter(
    (count) => count > 0,
  );

  return (
    <span
      aria-hidden
      className="flex h-11 w-9 shrink-0 flex-col justify-around rounded-md bg-emerald-800 p-1"
    >
      {rows.map((count, rowIndex) => (
        <span key={rowIndex} className="flex justify-around">
          {Array.from({ length: count }, (_, dot) => (
            <span key={dot} className="size-1.5 rounded-full bg-white" />
          ))}
        </span>
      ))}
    </span>
  );
}

type FormationPickerProps = {
  value: Formation;
  onChange: (formation: Formation) => void;
};

export function FormationPicker({ value, onChange }: FormationPickerProps) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="text-body-sm font-medium">Formação</legend>
      <p className="text-caption text-muted-foreground">
        Os números contam os jogadores de linha, de trás para a frente. O
        goleiro fica fora da conta.
      </p>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {FORMATIONS.map((option) => (
          <label
            key={option}
            className={cn(
              "flex cursor-pointer items-center gap-2.5 rounded-lg border bg-background p-2.5 shadow-xs",
              "has-checked:border-primary has-checked:bg-primary-soft has-focus-visible:ring-3 has-focus-visible:ring-ring/50",
            )}
          >
            <FormationIcon formation={option} />
            <span className="flex min-w-0 flex-col gap-0.5">
              <span className="flex items-center gap-1.5 text-body-sm font-medium">
                <input
                  type="radio"
                  name="formation"
                  value={option}
                  checked={value === option}
                  onChange={() => onChange(option)}
                  className="accent-primary"
                />
                {option}
              </span>
              <span className="text-caption text-muted-foreground">
                {describeFormation(option)}
              </span>
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}

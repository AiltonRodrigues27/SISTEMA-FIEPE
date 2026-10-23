import { FieldMessage } from "@/components/shared/field-message";
import { POSITION_LABELS } from "@/utils/labels";

type PositionCardsProps = {
  value: string;
  onChange: (position: string) => void;
  isLocked: boolean;
  error?: string;
};

export function PositionCards({
  value,
  onChange,
  isLocked,
  error,
}: PositionCardsProps) {
  return (
    <fieldset disabled={isLocked} className="flex flex-col gap-1.5">
      <legend className="mb-1.5 text-body-sm font-medium">Posição</legend>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
        {Object.entries(POSITION_LABELS).map(([position, label]) => (
          <label
            key={position}
            className="flex cursor-pointer flex-col items-center rounded-lg border bg-background px-1 py-2 shadow-xs has-checked:border-primary has-checked:bg-primary-soft has-focus-visible:ring-3 has-focus-visible:ring-ring/50 has-[input:disabled:not(:checked)]:cursor-not-allowed has-[input:disabled:not(:checked)]:opacity-50"
          >
            <input
              type="radio"
              name="position"
              value={position}
              checked={value === position}
              onChange={() => onChange(position)}
              className="sr-only"
            />
            <span className="text-body-sm font-medium">{position}</span>
            <span className="text-caption text-muted-foreground">{label}</span>
          </label>
        ))}
      </div>
      {isLocked && (
        <>
          <input type="hidden" name="position" value={value} />
          <p className="text-caption text-muted-foreground">
            Jogador com clube não muda de posição: as outras posições ficam
            desabilitadas.
          </p>
        </>
      )}
      <FieldMessage id="position-message" error={error} />
    </fieldset>
  );
}

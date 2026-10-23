import { Gauge } from "lucide-react";
import { AttributeBar } from "@/components/players/attribute-bar";
import type { AttributeScore, PlayerFormValues } from "@/types/players.types";
import { TECHNICAL_ATTRIBUTES } from "@/utils/player-attributes";

function toScore(text: string | undefined): AttributeScore {
  if (!text) return null;

  const number = Number(text);
  return Number.isInteger(number) && number >= 1 && number <= 99
    ? number
    : "invalid";
}

export function AttributePreview({ draft }: { draft: PlayerFormValues }) {
  const scores = TECHNICAL_ATTRIBUTES.map((attribute) => ({
    ...attribute,
    score: toScore(draft[attribute.name]),
  }));
  const potential = toScore(draft.potential);
  const hasInvalidValue =
    potential === "invalid" || scores.some(({ score }) => score === "invalid");

  return (
    <aside className="flex flex-col gap-3 rounded-lg border bg-muted-subtle p-3">
      <p className="flex items-center gap-2 text-caption font-medium">
        <Gauge className="size-3.5 text-muted-foreground" aria-hidden />
        Prévia dos atributos
      </p>
      {hasInvalidValue ? (
        <p className="py-8 text-center text-caption text-muted-foreground">
          Corrija os valores destacados para ver a prévia.
        </p>
      ) : (
        <>
          <div className="flex flex-col gap-2">
            {scores.map(({ name, label, score }) => (
              <AttributeBar
                key={name}
                label={label}
                value={typeof score === "number" ? score : null}
                potential={
                  typeof potential === "number" ? potential : undefined
                }
              />
            ))}
          </div>
          <p className="text-caption text-muted-foreground">
            Faixa clara: até o potencial
            {typeof potential === "number" ? ` (${potential})` : ""}. A prévia
            só desenha os valores digitados; não calcula overall nem valor base.
          </p>
        </>
      )}
    </aside>
  );
}

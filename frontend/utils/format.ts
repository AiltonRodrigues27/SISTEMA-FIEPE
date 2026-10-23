const BRASILIA_TIME_ZONE = "America/Sao_Paulo";
const BRASILIA_UTC_OFFSET = "-03:00";

const moneyFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
  timeZone: BRASILIA_TIME_ZONE,
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

// hourCycle h23 evita "24:05" à meia-noite em alguns motores.
const timeFormatter = new Intl.DateTimeFormat("pt-BR", {
  timeZone: BRASILIA_TIME_ZONE,
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

export function pluralize(
  count: number,
  singular: string,
  plural: string,
): string {
  return count === 1 ? singular : plural;
}

export function getInitials(name: string): string {
  const words = name.trim().split(/\s+/);
  const first = words[0]?.charAt(0) ?? "";
  const last = words.length > 1 ? (words.at(-1)?.charAt(0) ?? "") : "";

  return (first + last).toUpperCase();
}

export function formatMoney(value: number): string {
  return moneyFormatter.format(value);
}

export function formatSignedMoney(value: number): string {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "";

  return `${sign}${moneyFormatter.format(Math.abs(value))}`;
}

export function formatDate(isoDateTime: string): string {
  return dateFormatter.format(new Date(isoDateTime));
}

export function formatTime(isoDateTime: string): string {
  return timeFormatter.format(new Date(isoDateTime));
}

export function formatNow(): string {
  const now = new Date().toISOString();

  return `${formatDate(now)}, ${formatTime(now)}`;
}

// O input datetime-local entrega "2027-03-02T10:15", sem fuso: vale como horário de Brasília.
export function toApiDateTime(localDateTime: string): string {
  return `${localDateTime}${BRASILIA_UTC_OFFSET}`;
}

export function formatRange(
  min: string,
  max: string,
  format: (value: number) => string,
): string {
  if (min && max) return `${format(Number(min))} a ${format(Number(max))}`;
  if (min) return `a partir de ${format(Number(min))}`;
  return `até ${format(Number(max))}`;
}

export function formatSignedInteger(value: number): string {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "";

  return `${sign}${Math.abs(value)}`;
}

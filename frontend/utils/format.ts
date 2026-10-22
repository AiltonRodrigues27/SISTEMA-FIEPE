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

export function formatMoney(value: number): string {
  return moneyFormatter.format(value);
}

export function formatDateTime(isoDateTime: string): string {
  const date = new Date(isoDateTime);

  return `${dateFormatter.format(date)} ${timeFormatter.format(date)}`;
}

// O input datetime-local entrega "2027-03-02T10:15", sem fuso: vale como horário de Brasília.
export function toApiDateTime(localDateTime: string): string {
  return `${localDateTime}${BRASILIA_UTC_OFFSET}`;
}

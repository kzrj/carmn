/** ISO с сервера без таймзоны считаем UTC. */
export function parseServerDate(value: string | Date): Date {
  if (value instanceof Date) return value;
  const s = value.trim();
  if (!s) return new Date(NaN);
  if (/[Zz]$|[+-]\d{2}:?\d{2}$/.test(s)) return new Date(s);
  return new Date(`${s}Z`);
}

export function formatServerDate(
  value: string | Date | null | undefined,
  options: Intl.DateTimeFormatOptions = dateTimePreset,
  locale = "mn-MN"
): string {
  if (value == null || value === "") return "";
  const d = parseServerDate(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString(locale, options);
}

export const dateTimePreset: Intl.DateTimeFormatOptions = {
  day: "numeric",
  month: "long",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
};

export const dateTimeShortPreset: Intl.DateTimeFormatOptions = {
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
};

/** Значение для input[type=datetime-local] в локальной зоне. */
export function toDateTimeLocalInput(value?: string | Date): string {
  const d = value == null ? new Date() : parseServerDate(value);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** Локальный ввод datetime-local → ISO UTC для API. */
export function dateTimeLocalToServerIso(localValue: string): string {
  return new Date(localValue).toISOString();
}

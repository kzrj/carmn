import { formatServerDate, parseServerDate, dateTimePreset } from "../lib/serverDate";

type Props = {
  value: string | Date | null | undefined;
  options?: Intl.DateTimeFormatOptions;
  locale?: string;
  fallback?: string;
  className?: string;
};

/** Серверное время (UTC) → локальное отображение. */
export default function LocalDateTime({
  value,
  options = dateTimePreset,
  locale = "mn-MN",
  fallback = "—",
  className,
}: Props) {
  if (value == null || value === "") {
    return <span className={className}>{fallback}</span>;
  }
  const d = parseServerDate(value);
  if (Number.isNaN(d.getTime())) {
    return <span className={className}>{fallback}</span>;
  }
  return <span className={className}>{d.toLocaleString(locale, options)}</span>;
}

export { formatServerDate };

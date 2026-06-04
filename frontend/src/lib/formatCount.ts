import type { Locale } from "../types";

export function formatCount(value: number, locale: Locale): string {
  const tag = locale === "mn" ? "mn-MN" : locale === "ru" ? "ru-RU" : "en-US";
  return value.toLocaleString(tag);
}

export function formatYearRange(
  from: number | null | undefined,
  to: number | null | undefined,
): string | null {
  if (from == null && to == null) return null;
  if (from != null && to != null && from !== to) return `${from}—${to}`;
  return String(from ?? to);
}

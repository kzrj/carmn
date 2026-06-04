import type { Locale, LocalizedName } from "../types";

const STORAGE_KEY = "drom.locale";

export function getLocale(): Locale {
  const v = localStorage.getItem(STORAGE_KEY);
  if (v === "ru" || v === "en" || v === "mn") return v;
  return "ru";
}

export function setLocale(locale: Locale): void {
  localStorage.setItem(STORAGE_KEY, locale);
}

export function pickName(name: LocalizedName, locale: Locale = getLocale()): string {
  return name[locale] || name.mn || name.ru || name.en || "";
}

/** Drom auto.drom.ru: current year down to 1940. */
export const YEAR_MIN = 1940;

export function buildYearPresets(maxYear = new Date().getFullYear()): number[] {
  return Array.from({ length: maxYear - YEAR_MIN + 1 }, (_, i) => maxYear - i);
}

export const YEAR_PRESETS: number[] = buildYearPresets();

export function yearFilterOptions(): { value: string; label: string }[] {
  return YEAR_PRESETS.map((year) => ({
    value: String(year),
    label: String(year),
  }));
}

/** Engine volume presets like auto.drom.ru (0.7–6.0 л, step 0.1). */
export const ENGINE_VOLUME_PRESETS: number[] = Array.from({ length: 54 }, (_, i) =>
  Math.round((0.7 + i * 0.1) * 10) / 10,
);

/** Common MNT price steps for filter presets (currency kept as ₮). */
export const PRICE_PRESETS_MNT: number[] = [
  1_000_000, 2_000_000, 3_000_000, 5_000_000, 7_000_000, 10_000_000, 15_000_000, 20_000_000,
  25_000_000, 30_000_000, 40_000_000, 50_000_000, 75_000_000, 100_000_000, 150_000_000,
  200_000_000, 300_000_000, 500_000_000,
];

export function formatYearPreset(value: number): string {
  return String(value);
}

export function formatEngineVolumePreset(value: number): string {
  return `${value.toFixed(1).replace(".0", "")} л`;
}

export function formatPricePresetMnt(value: number): string {
  if (value >= 1_000_000) {
    const millions = value / 1_000_000;
    return `${Number.isInteger(millions) ? millions : millions.toFixed(1).replace(".0", "")} млн ₮`;
  }
  return `${value.toLocaleString("ru-RU")} ₮`;
}

export const TRANSMISSION_GROUP_LABELS: Record<string, { ru: string; mn: string; en: string }> = {
  automatic: { ru: "Автомат", mn: "Автомат", en: "Automatic" },
};

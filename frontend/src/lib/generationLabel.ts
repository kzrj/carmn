import type { Generation } from "../types";
import { getLocale, pickName } from "./i18n";

/** Drom-style label: «2 поколение, рестайлинг (2010–2016)». */
export function formatGenerationLabel(generation: Generation, locale = getLocale()): string {
  const info = (generation.generation_info || pickName(generation.name, locale)).trim();
  if (!info) return "";

  const { year_from: from, year_to: to } = generation;
  if (from && to) return `${info} (${from}–${to})`;
  if (from) return `${info} (${from}–)`;
  return info;
}

export function generationSelectOptions(generations: Generation[], locale = getLocale()) {
  return generations.map((generation) => ({
    value: String(generation.id),
    label: formatGenerationLabel(generation, locale),
  }));
}

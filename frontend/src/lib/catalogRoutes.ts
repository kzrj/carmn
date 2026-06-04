import type { Brand, Generation, ListingFilters, VehicleModel } from "../types";
import { filtersToSearchParams } from "./listingFilters";

export const RESERVED_PATHS = new Set(["login", "register", "listing", "sell"]);

export type CatalogPath = {
  brandSlug: string | null;
  modelSlug: string | null;
  generationSlug: string | null;
};

export function parseCatalogPath(pathname: string): CatalogPath {
  const parts = pathname.replace(/^\//, "").split("/").filter(Boolean);
  if (parts.length === 0 || RESERVED_PATHS.has(parts[0])) {
    return { brandSlug: null, modelSlug: null, generationSlug: null };
  }
  return {
    brandSlug: parts[0] ?? null,
    modelSlug: parts[1] ?? null,
    generationSlug: parts[2] ?? null,
  };
}

export function modelPathSlug(modelSlug: string, brandSlug: string): string {
  const prefix = `${brandSlug}-`;
  return modelSlug.startsWith(prefix) ? modelSlug.slice(prefix.length) : modelSlug;
}

export function modelDbSlug(brandSlug: string, pathSlug: string): string {
  return pathSlug.startsWith(`${brandSlug}-`) ? pathSlug : `${brandSlug}-${pathSlug}`;
}

export function generationPathSlug(
  generationSlug: string,
  brandSlug: string,
  modelUrlSlug: string,
): string {
  const prefix = `${modelDbSlug(brandSlug, modelUrlSlug)}-`;
  return generationSlug.startsWith(prefix) ? generationSlug.slice(prefix.length) : generationSlug;
}

export function generationDbSlug(
  brandSlug: string,
  modelUrlSlug: string,
  pathSlug: string,
): string {
  const modelSlug = modelDbSlug(brandSlug, modelUrlSlug);
  return pathSlug.startsWith(`${modelSlug}-`) ? pathSlug : `${modelSlug}-${pathSlug}`;
}

export function findModelByPathSlug(
  models: VehicleModel[],
  brandSlug: string,
  pathSlug: string,
): VehicleModel | undefined {
  const dbSlug = modelDbSlug(brandSlug, pathSlug);
  return models.find(
    (model) =>
      model.slug === dbSlug ||
      model.slug === pathSlug ||
      modelPathSlug(model.slug, brandSlug) === pathSlug,
  );
}

export function findGenerationByPathSlug(
  generations: Generation[],
  brandSlug: string,
  modelUrlSlug: string,
  pathSlug: string,
): Generation | undefined {
  const dbSlug = generationDbSlug(brandSlug, modelUrlSlug, pathSlug);
  return generations.find(
    (generation) =>
      generation.slug === dbSlug ||
      generation.slug === pathSlug ||
      generationPathSlug(generation.slug, brandSlug, modelUrlSlug) === pathSlug,
  );
}

export function buildCatalogPathname(
  filters: ListingFilters,
  brands: Brand[],
  models: VehicleModel[],
  generations: Generation[],
): string {
  if (!filters.brand) return "/";

  const brand = brands.find((item) => String(item.id) === filters.brand);
  if (!brand) return "/";

  let pathname = `/${brand.slug}`;
  if (!filters.model) return pathname;

  const model = models.find((item) => String(item.id) === filters.model);
  if (!model) return pathname;

  const modelUrlSlug = modelPathSlug(model.slug, brand.slug);
  pathname += `/${modelUrlSlug}`;
  if (!filters.generation) return pathname;

  const generation = generations.find((item) => String(item.id) === filters.generation);
  if (!generation) return pathname;

  pathname += `/${generationPathSlug(generation.slug, brand.slug, modelUrlSlug)}`;
  return pathname;
}

export function filtersToRoute(
  filters: ListingFilters,
  brands: Brand[],
  models: VehicleModel[],
  generations: Generation[],
): { pathname: string; search: string } {
  const params = filtersToSearchParams({
    ...filters,
    brand: "",
    model: "",
    generation: "",
  });
  return {
    pathname: buildCatalogPathname(filters, brands, models, generations),
    search: params.toString(),
  };
}

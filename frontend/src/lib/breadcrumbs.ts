import type { Brand, Generation, ListingDetail, ListingFilters, VehicleModel } from "../types";
import type { BreadcrumbItem } from "../components/layout/Breadcrumbs";
import {
  buildCatalogPathname,
  generationPathSlug,
  modelPathSlug,
} from "./catalogRoutes";
import { formatGenerationLabel } from "./generationLabel";
import { getLocale, pickName } from "./i18n";

export { formatGenerationLabel } from "./generationLabel";

export function buildCatalogBreadcrumbs(
  filters: ListingFilters,
  brands: Brand[],
  models: VehicleModel[],
  generations: Generation[],
  locale = getLocale(),
): BreadcrumbItem[] {
  if (!filters.brand) return [];

  const brand = brands.find((item) => String(item.id) === filters.brand);
  if (!brand) return [];

  const brandPath = `/${brand.slug}`;
  if (!filters.model) {
    return [{ label: pickName(brand.name, locale) }];
  }

  const model = models.find((item) => String(item.id) === filters.model);
  if (!model) {
    return [{ label: pickName(brand.name, locale), to: brandPath }];
  }

  const modelUrlSlug = modelPathSlug(model.slug, brand.slug);
  const modelPath = `/${brand.slug}/${modelUrlSlug}`;
  if (!filters.generation) {
    return [
      { label: pickName(brand.name, locale), to: brandPath },
      { label: pickName(model.name, locale) },
    ];
  }

  const generation = generations.find((item) => String(item.id) === filters.generation);
  if (!generation) {
    return [
      { label: pickName(brand.name, locale), to: brandPath },
      { label: pickName(model.name, locale), to: modelPath },
    ];
  }

  const generationPath = buildCatalogPathname(filters, brands, models, generations);
  return [
    { label: pickName(brand.name, locale), to: brandPath },
    { label: pickName(model.name, locale), to: modelPath },
    { label: formatGenerationLabel(generation, locale), to: generationPath },
  ];
}

export function buildListingBreadcrumbs(item: ListingDetail, locale = getLocale()): BreadcrumbItem[] {
  const brand = item.brand;
  const model = item.model;
  const brandPath = `/${brand.slug}`;
  const modelUrlSlug = modelPathSlug(model.slug, brand.slug);
  const modelPath = `/${brand.slug}/${modelUrlSlug}`;
  const title = `${pickName(brand.name, locale)} ${pickName(model.name, locale)}, ${item.year}`;

  const crumbs: BreadcrumbItem[] = [
    { label: pickName(brand.name, locale), to: brandPath },
    { label: pickName(model.name, locale), to: modelPath },
  ];

  if (item.generation) {
    const generationUrlSlug = generationPathSlug(item.generation.slug, brand.slug, modelUrlSlug);
    crumbs.push({
      label: formatGenerationLabel(item.generation, locale),
      to: `${modelPath}/${generationUrlSlug}`,
    });
  }

  crumbs.push({ label: title });
  return crumbs;
}

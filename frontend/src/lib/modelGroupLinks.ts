import type { ListingFilters, ListingModelGroup } from "../types";
import { buildCatalogPathname } from "./catalogRoutes";
import { defaultListingFilters, filtersToSearchParams } from "./listingFilters";

export function modelGroupTargetFilters(
  group: ListingModelGroup,
  current: ListingFilters,
): ListingFilters {
  return {
    ...current,
    page: "1",
    view: "listings",
    brand: String(group.brand.id),
    model: String(group.model.id),
    generation: group.generation ? String(group.generation.id) : "",
    trim: group.trim ? String(group.trim.id) : "",
  };
}

export function modelGroupToLocation(
  group: ListingModelGroup,
  current: ListingFilters,
): { pathname: string; search: string } {
  const filters = modelGroupTargetFilters(group, current);
  const brands = [group.brand];
  const models = [{ ...group.model, brand_id: group.brand.id }];
  const generations = group.generation ? [group.generation] : [];
  const pathname = buildCatalogPathname(filters, brands, models, generations);
  const params = filtersToSearchParams({
    ...filters,
    brand: "",
    model: "",
    generation: "",
  });
  return { pathname, search: params.toString() };
}

export function isDefaultCatalogView(filters: ListingFilters): boolean {
  return filters.view === defaultListingFilters().view;
}

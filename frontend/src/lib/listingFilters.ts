import type { ListingFilters } from "../types";

export { filtersToRoute, parseCatalogPath, RESERVED_PATHS } from "./catalogRoutes";

export const defaultListingFilters = (): ListingFilters => ({
  brand: "",
  model: "",
  generation: "",
  trim: "",
  city: "",
  region: "",
  radius_km: "",
  condition: "",
  price_min: "",
  price_max: "",
  year_min: "",
  year_max: "",
  mileage_min: "",
  mileage_max: "",
  engine_volume_min: "",
  engine_volume_max: "",
  power_min: "",
  power_max: "",
  fuel: "",
  transmission: "",
  drive: "",
  body_type: "",
  color: "",
  steering: "",
  pts_status: "",
  damage_status: "",
  seller_type: "",
  availability: "",
  owners_count: "",
  import_country: "",
  brand_country: "",
  exchange_possible: false,
  is_certified: false,
  without_local_mileage: false,
  customs_cleared: false,
  has_photos: false,
  unsold: true,
  q: "",
  ordering: "-published_at",
  page: "1",
  view: "listings",
  groups_ordering: "-count",
});

const FILTER_KEYS = Object.keys(defaultListingFilters()) as (keyof ListingFilters)[];

/** Comma-separated body type ids, e.g. "1,3,5". */
export function parseBodyTypeFilter(raw: string): string[] {
  return raw
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

export function joinBodyTypeFilter(ids: string[]): string {
  return ids.join(",");
}

export function filtersToSearchParams(filters: ListingFilters): URLSearchParams {
  const p = new URLSearchParams();
  for (const key of FILTER_KEYS) {
    const val = filters[key];
    if (key === "body_type") {
      for (const id of parseBodyTypeFilter(String(val ?? ""))) {
        p.append("body_type", id);
      }
      continue;
    }
    if (typeof val === "boolean") {
      if (val) p.set(key, "true");
    } else if (val !== "" && val != null) {
      p.set(key, String(val));
    }
  }
  return p;
}

export function searchParamsToFilters(params: URLSearchParams): ListingFilters {
  const base = defaultListingFilters();
  for (const key of FILTER_KEYS) {
    if (key === "body_type") {
      const ids = params.getAll("body_type").flatMap((item) => parseBodyTypeFilter(item));
      if (ids.length) base.body_type = joinBodyTypeFilter([...new Set(ids)]);
      continue;
    }
    if (!params.has(key)) continue;
    const raw = params.get(key)!;
    if (typeof base[key] === "boolean") {
      (base as Record<string, unknown>)[key] = raw === "true";
    } else {
      (base as Record<string, unknown>)[key] = raw;
    }
  }
  return base;
}

export function filtersToQueryString(filters: ListingFilters): string {
  const p = filtersToSearchParams(filters);
  const s = p.toString();
  return s ? `?${s}` : "";
}

const POPULAR_BRANDS_IGNORE: (keyof ListingFilters)[] = ["view", "groups_ordering", "page", "ordering"];

export function hasActiveFilters(filters: ListingFilters): boolean {
  const defaults = defaultListingFilters();
  for (const key of FILTER_KEYS) {
    if (POPULAR_BRANDS_IGNORE.includes(key)) continue;
    if (filters[key] !== defaults[key]) return true;
  }
  return false;
}

/** API query object — skip empty values and false booleans. */
export function filtersToApiParams(filters: ListingFilters): Record<string, string> {
  const out: Record<string, string> = {};
  for (const key of FILTER_KEYS) {
    const val = filters[key];
    if (key === "body_type") {
      const ids = parseBodyTypeFilter(String(val ?? ""));
      if (ids.length) out.body_type = joinBodyTypeFilter(ids);
      continue;
    }
    if (typeof val === "boolean") {
      if (val) out[key] = "true";
    } else if (val !== "" && val != null) {
      out[key] = String(val);
    }
  }
  return out;
}

const LISTING_API_SKIP = new Set(["view", "groups_ordering"]);

/** Params for flat `/listings/` (excludes catalog view mode). */
export function filtersToListingApiParams(filters: ListingFilters): Record<string, string> {
  const out = filtersToApiParams(filters);
  for (const key of LISTING_API_SKIP) {
    delete out[key];
  }
  return out;
}

/** Model lineup is unavailable when a trim is already selected. */
export function canUseModelGroupsView(filters: ListingFilters): boolean {
  return !filters.trim;
}

export function filtersEqual(a: ListingFilters, b: ListingFilters): boolean {
  for (const key of FILTER_KEYS) {
    if (a[key] !== b[key]) return false;
  }
  return true;
}

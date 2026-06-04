export type Locale = "mn" | "ru" | "en";

export type LocalizedName = {
  mn: string;
  ru: string;
  en: string;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
  model_groups_count?: number;
};

export type RefItem = {
  id: number;
  slug: string;
  name: LocalizedName;
};

export type TransmissionRef = RefItem & {
  group?: string | null;
};

export type Country = RefItem & { iso_code?: string };

export type City = RefItem & {
  region: RefItem;
  latitude: string;
  longitude: string;
};

export type Brand = RefItem & {
  country: Country | null;
  icon: string | null;
};

export type VehicleModel = RefItem & {
  brand_id: number;
};

export type Generation = RefItem & {
  model_id: number;
  generation_info: string;
  year_from: number | null;
  year_to: number | null;
  body_type_id: number | null;
};

export type Trim = RefItem & {
  generation_id: number;
  body_type_id: number | null;
  fuel_id: number | null;
  transmission_id: number | null;
  drive_id: number | null;
};

export type ListingCreatePayload = {
  brand_id: number;
  model_id: number;
  generation_id?: number | null;
  trim_id?: number | null;
  city_id: number;
  year: number;
  price?: number;
  price_usd?: number;
  mileage?: number | null;
  condition_type: "new" | "used";
  body_type?: number | null;
  fuel?: number | null;
  transmission?: number | null;
  drive?: number | null;
  vin?: string;
  chassis_number?: string;
  description?: string;
};

export type ListingModelGroup = {
  count: number;
  min_price: number | null;
  max_price: number | null;
  year_from: number | null;
  year_to: number | null;
  photos: string[];
  specs_summary: string;
  brand: Brand;
  model: VehicleModel;
  generation: Generation | null;
  trim: Trim | null;
};

export type ListingModelGroupsResponse = {
  count: number;
  listings_count: number;
  dimension: "model" | "generation" | "trim";
  results: ListingModelGroup[];
};

export type ListingListItem = {
  id: number;
  brand: Brand;
  model: VehicleModel;
  year: number;
  price: number;
  mileage: number | null;
  condition_type: "new" | "used";
  status: "active" | "sold";
  city: City;
  seller_type: "owner" | "private" | "company";
  steering: "left" | "right";
  published_at: string;
  primary_photo: string | null;
  has_photos: boolean;
};

export type ListingPhoto = {
  id: number;
  image: string;
  sort_order: number;
  is_primary: boolean;
};

export type ListingDetail = ListingListItem & {
  generation: Generation | null;
  trim: Trim | null;
  body_type: RefItem | null;
  color: RefItem | null;
  fuel: RefItem | null;
  transmission: RefItem | null;
  drive: RefItem | null;
  engine_volume: string | null;
  power_hp: number | null;
  pts_status: string;
  damage_status: string;
  availability: string;
  owners_count: string | null;
  exchange_possible: boolean;
  is_certified: boolean;
  without_local_mileage: boolean;
  customs_cleared: boolean;
  import_country: Country | null;
  description: string;
  updated_at: string;
  photos: ListingPhoto[];
  user: {
    id: number;
    phone: string;
    seller_profile: {
      seller_type: string;
      display_name: string;
      company_name: string;
    };
  };
};

export type ListingFilters = {
  brand: string;
  model: string;
  generation: string;
  trim: string;
  city: string;
  region: string;
  radius_km: string;
  condition: "" | "new" | "used";
  price_min: string;
  price_max: string;
  year_min: string;
  year_max: string;
  mileage_min: string;
  mileage_max: string;
  engine_volume_min: string;
  engine_volume_max: string;
  power_min: string;
  power_max: string;
  fuel: string;
  transmission: string;
  drive: string;
  body_type: string;
  color: string;
  steering: string;
  pts_status: string;
  damage_status: string;
  seller_type: string;
  availability: string;
  owners_count: string;
  import_country: string;
  brand_country: string;
  exchange_possible: boolean;
  is_certified: boolean;
  without_local_mileage: boolean;
  customs_cleared: boolean;
  has_photos: boolean;
  unsold: boolean;
  q: string;
  ordering: string;
  page: string;
  view: "listings" | "models";
  groups_ordering: "-count" | "count" | "name";
};

export type AuthTokens = {
  access: string;
  refresh: string;
};

export type UserMe = {
  id: number;
  phone: string;
  seller_profile: {
    seller_type: string;
    display_name: string;
    company_name: string;
  };
};

export type ReferenceBundle = {
  regions: RefItem[];
  cities: City[];
  brands: Brand[];
  bodyTypes: RefItem[];
  colors: RefItem[];
  fuelTypes: RefItem[];
  transmissions: TransmissionRef[];
  driveTypes: RefItem[];
  countries: Country[];
};

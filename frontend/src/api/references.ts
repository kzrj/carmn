import type {
  Brand,
  Country,
  Generation,
  RefItem,
  ReferenceBundle,
  TransmissionRef,
  VehicleModel,
  Trim,
  City,
} from "../types";
import { fetchList } from "./fetchList";

export async function fetchReferenceBundle(): Promise<ReferenceBundle> {
  const [regions, cities, brands, bodyTypes, colors, fuelTypes, transmissions, driveTypes, countries] =
    await Promise.all([
      fetchList<RefItem>("/regions/"),
      fetchList<City>("/cities/"),
      fetchList<Brand>("/brands/"),
      fetchList<RefItem>("/body-types/"),
      fetchList<RefItem>("/colors/"),
      fetchList<RefItem>("/fuel-types/"),
      fetchList<TransmissionRef>("/transmissions/"),
      fetchList<RefItem>("/drive-types/"),
      fetchList<Country>("/countries/"),
    ]);
  return { regions, cities, brands, bodyTypes, colors, fuelTypes, transmissions, driveTypes, countries };
}

export function fetchModels(brandId: number): Promise<VehicleModel[]> {
  return fetchList("/models/", { brand: String(brandId) });
}

export function fetchGenerations(modelId: number): Promise<Generation[]> {
  return fetchList("/generations/", { model: String(modelId) });
}

export function fetchTrims(generationId: number): Promise<Trim[]> {
  return fetchList("/trims/", { generation: String(generationId) });
}

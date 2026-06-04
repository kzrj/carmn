import type { Generation, ListingCreatePayload, Trim } from "../types";

export type SpecFields = {
  bodyType: string;
  fuel: string;
  transmission: string;
  drive: string;
};

export const emptySpecs = (): SpecFields => ({
  bodyType: "",
  fuel: "",
  transmission: "",
  drive: "",
});

export function yearOptions(generation: Generation | null): number[] {
  const now = new Date().getFullYear();
  const from = generation?.year_from ?? 1980;
  const to = generation?.year_to ?? now;
  const years: number[] = [];
  for (let y = to; y >= from; y--) years.push(y);
  return years;
}

export function specsFromGeneration(generation: Generation | null): SpecFields {
  if (!generation) return emptySpecs();
  return {
    ...emptySpecs(),
    bodyType: generation.body_type_id ? String(generation.body_type_id) : "",
  };
}

export function specsFromTrim(trim: Trim | null, generation: Generation | null): SpecFields {
  if (!trim) return specsFromGeneration(generation);
  return {
    bodyType: trim.body_type_id ? String(trim.body_type_id) : "",
    fuel: trim.fuel_id ? String(trim.fuel_id) : "",
    transmission: trim.transmission_id ? String(trim.transmission_id) : "",
    drive: trim.drive_id ? String(trim.drive_id) : "",
  };
}

type BuildPayloadInput = {
  brandId: string;
  modelId: string;
  generationId: string;
  trimId: string;
  year: string;
  condition: "new" | "used";
  mileage: string;
  specs: SpecFields;
  vin: string;
  chassis: string;
  description: string;
  priceMode: "mnt" | "usd";
  price: string;
  cityId: string;
};

export function buildListingPayload(input: BuildPayloadInput): ListingCreatePayload {
  const payload: ListingCreatePayload = {
    brand_id: Number(input.brandId),
    model_id: Number(input.modelId),
    city_id: Number(input.cityId),
    year: Number(input.year),
    condition_type: input.condition,
  };

  if (input.generationId) payload.generation_id = Number(input.generationId);
  if (input.trimId) payload.trim_id = Number(input.trimId);
  if (input.mileage) payload.mileage = Number(input.mileage);
  if (input.vin.trim()) payload.vin = input.vin.trim();
  if (input.chassis.trim()) payload.chassis_number = input.chassis.trim();
  if (input.description.trim()) payload.description = input.description.trim();

  if (input.specs.bodyType) payload.body_type = Number(input.specs.bodyType);
  if (input.specs.fuel) payload.fuel = Number(input.specs.fuel);
  if (input.specs.transmission) payload.transmission = Number(input.specs.transmission);
  if (input.specs.drive) payload.drive = Number(input.specs.drive);

  if (input.priceMode === "usd") {
    payload.price_usd = Number(input.price);
  } else {
    payload.price = Number(input.price);
  }

  return payload;
}

export function formatApiError(err: unknown): string {
  if (!(err instanceof Error)) return "Unknown error";
  return err.message;
}

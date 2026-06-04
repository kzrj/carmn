import type {
  ListingCreatePayload,
  ListingDetail,
  ListingFilters,
  ListingListItem,
  ListingModelGroupsResponse,
  ListingPhoto,
  Paginated,
} from "../types";
import { filtersToApiParams, filtersToListingApiParams } from "../lib/listingFilters";
import { apiFetch } from "./client";

export function fetchListings(filters: ListingFilters): Promise<Paginated<ListingListItem>> {
  return apiFetch("/listings/", { params: filtersToListingApiParams(filters) });
}

export function fetchModelGroups(filters: ListingFilters): Promise<ListingModelGroupsResponse> {
  return apiFetch("/listings/model-groups/", { params: filtersToApiParams(filters) });
}

export function fetchListing(id: number): Promise<ListingDetail> {
  return apiFetch(`/listings/${id}/`);
}

export function createListing(data: ListingCreatePayload): Promise<ListingDetail> {
  return apiFetch("/listings/", { method: "POST", body: JSON.stringify(data) });
}

export function uploadListingPhoto(listingId: number, file: File): Promise<ListingPhoto> {
  const body = new FormData();
  body.append("image", file);
  return apiFetch(`/listings/${listingId}/photos/`, { method: "POST", body });
}

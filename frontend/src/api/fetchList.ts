import type { Paginated } from "../types";
import { apiFetch } from "./client";

export async function fetchList<T>(path: string, params?: Record<string, string>): Promise<T[]> {
  const data = await apiFetch<Paginated<T> | T[]>(path, { params });
  return Array.isArray(data) ? data : data.results;
}

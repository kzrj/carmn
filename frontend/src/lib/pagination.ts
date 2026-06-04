/** Must match backend `PAGE_SIZE` in config/settings.py */
export const LISTINGS_PAGE_SIZE = 20;

export type PaginationItem = number | "ellipsis";

export function getPaginationItems(
  current: number,
  totalPages: number,
  siblingCount = 1,
): PaginationItem[] {
  if (totalPages <= 1) return [];

  const pages = new Set<number>([1, totalPages]);
  for (let p = current - siblingCount; p <= current + siblingCount; p++) {
    if (p >= 1 && p <= totalPages) pages.add(p);
  }

  const sorted = [...pages].sort((a, b) => a - b);
  const items: PaginationItem[] = [];

  for (let i = 0; i < sorted.length; i++) {
    if (i > 0 && sorted[i] - sorted[i - 1] > 1) {
      items.push("ellipsis");
    }
    items.push(sorted[i]);
  }

  return items;
}

export function getPageRange(page: number, total: number, pageSize = LISTINGS_PAGE_SIZE) {
  if (total === 0) return { from: 0, to: 0 };
  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);
  return { from, to };
}

export function formatPriceMnt(value: number): string {
  return `${value.toLocaleString("mn-MN")} ₮`;
}

export function formatMileage(km: number | null | undefined): string {
  if (km == null) return "—";
  return `${km.toLocaleString("mn-MN")} км`;
}

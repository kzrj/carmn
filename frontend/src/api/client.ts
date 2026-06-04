const BASE = "/api";
const TOKEN_KEY = "drom.access";
const REFRESH_KEY = "drom.refresh";

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

function buildUrl(path: string, params?: Record<string, string>): string {
  const url = `${BASE}${path}`;
  if (!params || Object.keys(params).length === 0) return url;
  const sp = new URLSearchParams(params);
  return `${url}?${sp.toString()}`;
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { params?: Record<string, string> },
): Promise<T> {
  const { params, ...rest } = init ?? {};
  const headers = new Headers(rest.headers);
  if (!headers.has("Content-Type") && rest.body && !(rest.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const token = getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(buildUrl(path, params), { ...rest, headers });
  if (!res.ok) {
    let msg = `Error (${res.status})`;
    try {
      const j = (await res.json()) as Record<string, unknown>;
      if (typeof j.detail === "string") {
        msg = j.detail;
      } else if (Array.isArray(j.detail)) {
        msg = j.detail.join(", ");
      } else {
        const parts = Object.entries(j).flatMap(([key, val]) => {
          if (Array.isArray(val)) return val.map((item) => `${key}: ${item}`);
          if (typeof val === "string") return [`${key}: ${val}`];
          return [];
        });
        if (parts.length) msg = parts.join("; ");
      }
    } catch {
      /* ignore */
    }
    throw new Error(msg);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

import type { AuthTokens, UserMe } from "../types";
import { apiFetch, clearTokens, setTokens } from "./client";

export function registerUser(body: {
  phone: string;
  password: string;
  seller_type: string;
  display_name?: string;
}): Promise<UserMe> {
  return apiFetch("/auth/register/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function loginUser(phone: string, password: string): Promise<AuthTokens> {
  const tokens = await apiFetch<AuthTokens>("/auth/token/", {
    method: "POST",
    body: JSON.stringify({ phone, password }),
  });
  setTokens(tokens.access, tokens.refresh);
  return tokens;
}

export function fetchMe(): Promise<UserMe> {
  return apiFetch("/auth/me/");
}

export function logoutUser(): void {
  clearTokens();
}

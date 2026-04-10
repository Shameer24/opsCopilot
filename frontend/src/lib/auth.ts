import { apiFetch } from "./api";
import type { AuthToken } from "./types";

const TOKEN_KEY = "opscopilot_token";
const SESSION_MODE_KEY = "opscopilot_session_mode";

export type SessionMode = "guest" | "account";

export function setToken(token: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(SESSION_MODE_KEY);
}

export function isAuthed(): boolean {
  return !!getToken();
}

export function setSessionMode(mode: SessionMode) {
  if (typeof window === "undefined") return;
  localStorage.setItem(SESSION_MODE_KEY, mode);
}

export function getSessionMode(): SessionMode | null {
  if (typeof window === "undefined") return null;
  const mode = localStorage.getItem(SESSION_MODE_KEY);
  return mode === "guest" || mode === "account" ? mode : null;
}

export function isGuestSession(): boolean {
  return getSessionMode() === "guest";
}

export async function ensureSession(): Promise<string> {
  const existing = getToken();
  if (existing) {
    if (!getSessionMode()) setSessionMode("account");
    return existing;
  }

  const nonce =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const email = `guest+${nonce}@opscopilot.local`;
  const password = `${nonce}-GuestOnly123!`;

  const res = await apiFetch<AuthToken>("/auth/register", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password }),
  });

  setToken(res.access_token);
  setSessionMode("guest");
  return res.access_token;
}

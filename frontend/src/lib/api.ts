import { getToken } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

type ApiErrorPayload = { detail?: string };

async function parseError(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as ApiErrorPayload;
    return data.detail || `Request failed (${res.status})`;
  } catch {
    return `Request failed (${res.status})`;
  }
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { auth?: boolean }
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers = new Headers(init?.headers || {});
  headers.set("Content-Type", headers.get("Content-Type") || "application/json");

  const auth = init?.auth ?? true;
  if (auth) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(url, {
    ...init,
    headers
  });

  if (!res.ok) {
    const msg = await parseError(res);
    throw new Error(msg);
  }

  return (await res.json()) as T;
}

export async function apiUpload(
  path: string,
  file: File
): Promise<{ document_id: string; status: string }> {
  const url = `${API_BASE}${path}`;
  const form = new FormData();
  form.append("file", file);

  const headers = new Headers();
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(url, {
    method: "POST",
    headers,
    body: form
  });

  if (!res.ok) {
    const msg = await parseError(res);
    throw new Error(msg);
  }

  return (await res.json()) as { document_id: string; status: string };
}
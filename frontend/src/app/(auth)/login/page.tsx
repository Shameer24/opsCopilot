"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { setToken } from "@/lib/auth";
import type { AuthToken } from "@/lib/types";
import Toast from "@/components/Toast";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      const res = await apiFetch<AuthToken>("/auth/login", {
        method: "POST",
        auth: false,
        body: JSON.stringify({ email, password })
      });
      setToken(res.access_token);
      router.replace("/documents");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setToast(err.message || "Login failed");
      } else {
        setToast("Login failed");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-md space-y-4">
      <h1 className="text-xl font-semibold">Login</h1>

      <form onSubmit={submit} className="bg-white border rounded-xl p-4 space-y-3">
        <div className="space-y-1">
          <label className="text-sm text-zinc-700">Email</label>
          <input
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            required
          />
        </div>

        <div className="space-y-1">
          <label className="text-sm text-zinc-700">Password</label>
          <input
            className="w-full border rounded-lg px-3 py-2 text-sm"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button
          disabled={busy}
          className="w-full px-4 py-2 rounded-lg bg-zinc-900 text-white text-sm disabled:opacity-60"
        >
          {busy ? "Signing in..." : "Login"}
        </button>
      </form>

      <Toast message={toast} onClose={() => setToast(null)} />
    </div>
  );
}
"use client";

import { useEffect, useState } from "react";
import AuthGuard from "@/components/AuthGuard";
import DocumentTable from "@/components/DocumentTable";
import Toast from "@/components/Toast";
import { apiFetch } from "@/lib/api";
import type { DocumentOut } from "@/lib/types";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [busy, setBusy] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  async function load() {
    setBusy(true);
    try {
      const res = await apiFetch<DocumentOut[]>("/documents", { method: "GET" });
      setDocs(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load documents";
      setToast({ msg, ok: false });
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id: string) {
    const doc = docs.find((d) => d.id === id);
    if (!confirm(`Delete "${doc?.filename ?? id}"? This cannot be undone.`)) return;

    setDeleting(id);
    try {
      await apiFetch(`/documents/${id}`, { method: "DELETE" });
      setDocs((prev) => prev.filter((d) => d.id !== id));
      setToast({ msg: "Document deleted.", ok: true });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Delete failed";
      setToast({ msg, ok: false });
    } finally {
      setDeleting(null);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AuthGuard>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">Documents</h1>
            <p className="text-sm text-zinc-500 mt-0.5">
              {docs.length > 0 ? `${docs.length} document${docs.length !== 1 ? "s" : ""}` : ""}
            </p>
          </div>
          <button
            onClick={load}
            disabled={busy}
            className="text-sm px-3 py-2 rounded-lg bg-zinc-200 hover:bg-zinc-300 disabled:opacity-50 transition-colors"
          >
            {busy ? "Loading…" : "Refresh"}
          </button>
        </div>

        {busy && docs.length === 0 ? (
          <div className="text-sm text-zinc-400 py-8 text-center">Loading documents…</div>
        ) : (
          <DocumentTable docs={docs} onDelete={handleDelete} deleting={deleting} />
        )}

        {toast && (
          <Toast
            message={toast.msg}
            onClose={() => setToast(null)}
          />
        )}
      </div>
    </AuthGuard>
  );
}

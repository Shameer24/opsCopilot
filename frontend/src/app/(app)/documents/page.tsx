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
  const [toast, setToast] = useState<string | null>(null);

  async function load() {
    setBusy(true);
    try {
      const res = await apiFetch<DocumentOut[]>("/documents", { method: "GET" });
      setDocs(res);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setToast(err.message || "Failed to load documents");
      } else {
        setToast("Failed to load documents");
      }
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AuthGuard>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">Documents</h1>
          <button
            onClick={load}
            className="text-sm px-3 py-2 rounded-lg bg-zinc-200 hover:bg-zinc-300"
          >
            Refresh
          </button>
        </div>

        {busy ? (
          <div className="text-sm text-zinc-600">Loading...</div>
        ) : (
          <DocumentTable docs={docs} />
        )}

        <Toast message={toast} onClose={() => setToast(null)} />
      </div>
    </AuthGuard>
  );
}
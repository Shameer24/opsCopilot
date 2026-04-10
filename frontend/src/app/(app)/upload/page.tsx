"use client";

import { useState } from "react";
import AuthGuard from "@/components/AuthGuard";
import UploadDropzone from "@/components/UploadDropzone";
import Toast from "@/components/Toast";
import { apiUpload } from "@/lib/api";

export default function UploadPage() {
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  async function handleFile(file: File) {
    setBusy(true);
    setStatus(null);
    try {
      const res = await apiUpload("/documents/upload", file);
      setStatus(`Uploaded. Document ID: ${res.document_id}. Ingestion started.`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setToast(err.message || "Upload failed");
      } else {
        setToast("Upload failed");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthGuard>
      <div className="space-y-4">
        <h1 className="text-xl font-semibold">Upload</h1>

        <UploadDropzone onFile={handleFile} />

        {busy ? <div className="text-sm text-zinc-600">Uploading...</div> : null}
        {status ? (
          <div className="text-sm bg-zinc-100 border rounded-lg p-3">{status}</div>
        ) : null}

        <Toast message={toast} onClose={() => setToast(null)} />
      </div>
    </AuthGuard>
  );
}
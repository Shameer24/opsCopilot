"use client";

import AuthGuard from "@/components/AuthGuard";

const STACK = [
  { label: "Backend", value: "FastAPI + Python 3.11" },
  { label: "Database", value: "PostgreSQL 16 + pgvector" },
  { label: "Embeddings", value: "all-MiniLM-L6-v2 (384-dim, local)" },
  { label: "LLM", value: "Ollama (llama3.1) / retrieval-only fallback" },
  { label: "Frontend", value: "Next.js 15 + Tailwind CSS" },
  { label: "Auth", value: "JWT (HS256, 24 h expiry)" },
];

const RETRIEVAL = [
  { label: "Top-K chunks", value: "6" },
  { label: "Min similarity score", value: "0.10" },
  { label: "Chunk max size", value: "2 200 chars" },
  { label: "Chunk overlap", value: "200 chars" },
  { label: "Max upload", value: "25 MB" },
];

export default function SettingsPage() {
  return (
    <AuthGuard>
      <div className="space-y-6 max-w-xl">
        <div>
          <h1 className="text-xl font-semibold">Settings</h1>
          <p className="text-sm text-zinc-500 mt-1">
            Current runtime configuration — override via environment variables.
          </p>
        </div>

        <section className="space-y-2">
          <h2 className="text-sm font-semibold text-zinc-700 uppercase tracking-wide">Stack</h2>
          <div className="bg-white border rounded-xl divide-y text-sm">
            {STACK.map(({ label, value }) => (
              <div key={label} className="flex justify-between px-4 py-2.5">
                <span className="text-zinc-500">{label}</span>
                <span className="font-mono text-zinc-900">{value}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-semibold text-zinc-700 uppercase tracking-wide">
            Retrieval defaults
          </h2>
          <div className="bg-white border rounded-xl divide-y text-sm">
            {RETRIEVAL.map(({ label, value }) => (
              <div key={label} className="flex justify-between px-4 py-2.5">
                <span className="text-zinc-500">{label}</span>
                <span className="font-mono text-zinc-900">{value}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-zinc-400">
            Override via{" "}
            <code className="bg-zinc-100 px-1 rounded">TOP_K</code>,{" "}
            <code className="bg-zinc-100 px-1 rounded">MIN_SCORE</code> env vars on the backend.
          </p>
        </section>
      </div>
    </AuthGuard>
  );
}
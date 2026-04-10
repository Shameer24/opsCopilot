"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

export default function FeedbackButtons({ queryLogId }: { queryLogId: string }) {
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState<string | null>(null);

  async function send(rating: 1 | -1) {
    setBusy(true);
    try {
      await apiFetch("/feedback", {
        method: "POST",
        body: JSON.stringify({ query_log_id: queryLogId, rating })
      });
      setDone(rating === 1 ? "Thanks. Logged as helpful." : "Thanks. Logged as not helpful.");
    } catch {
      setDone("Feedback failed to submit.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <button
        disabled={busy}
        onClick={() => send(1)}
        className="text-sm px-3 py-2 rounded-lg bg-emerald-100 hover:bg-emerald-200 disabled:opacity-60"
      >
        👍 Helpful
      </button>
      <button
        disabled={busy}
        onClick={() => send(-1)}
        className="text-sm px-3 py-2 rounded-lg bg-red-100 hover:bg-red-200 disabled:opacity-60"
      >
        👎 Not helpful
      </button>
      {done ? <div className="text-xs text-zinc-600">{done}</div> : null}
    </div>
  );
}
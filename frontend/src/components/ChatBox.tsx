"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import type { AskResponse } from "@/lib/types";
import CitationList from "./CitationList";
import FeedbackButtons from "./FeedbackButtons";

export default function ChatBox() {
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [resp, setResp] = useState<AskResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function ask() {
    setErr(null);
    setBusy(true);
    setResp(null);
    try {
      const out = await apiFetch<AskResponse>("/chat/ask", {
        method: "POST",
        body: JSON.stringify({ question })
      });
      setResp(out);
    } catch (e: unknown ) {
      if (e instanceof Error) {
        setErr(e.message || "Ask failed");
      } else {
        setErr("Ask failed");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white border rounded-xl p-4 space-y-3">
        <div className="text-sm font-semibold">Ask your docs</div>

        <textarea
          className="w-full border rounded-lg px-3 py-2 text-sm min-h-[120px]"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Example: What are the top recurring error patterns and what do they usually indicate?"
        />

        <div className="flex items-center gap-2">
          <button
            onClick={ask}
            disabled={busy || !question.trim()}
            className="text-sm px-4 py-2 rounded-lg bg-zinc-900 text-white disabled:opacity-60"
          >
            {busy ? "Thinking..." : "Ask"}
          </button>
          {err ? <div className="text-sm text-red-700">{err}</div> : null}
        </div>
      </div>

      {resp ? (
        <div className="space-y-3">
          <div className="bg-white border rounded-xl p-4 space-y-3">
            <div className="text-sm font-semibold">Answer</div>
            <pre className="whitespace-pre-wrap text-sm text-zinc-800">{resp.answer_markdown}</pre>
            <FeedbackButtons queryLogId={resp.query_log_id} />
          </div>
          <CitationList citations={resp.citations} />
        </div>
      ) : null}
    </div>
  );
}
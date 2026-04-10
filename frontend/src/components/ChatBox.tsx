"use client";

import { useState, useRef, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import type { AskResponse } from "@/lib/types";
import CitationList from "./CitationList";
import FeedbackButtons from "./FeedbackButtons";

/** Minimal markdown → HTML renderer (bold, italic, code, headings, lists, paragraphs). */
function renderMarkdown(md: string): string {
  const lines = md.split("\n");
  const out: string[] = [];
  let inList = false;

  const escape = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  const inlineFormat = (s: string) =>
    escape(s)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/__(.+?)__/g, "<strong>$1</strong>")
      .replace(/_(.+?)_/g, "<em>$1</em>");

  for (const raw of lines) {
    const line = raw.trimEnd();

    // heading
    const hm = line.match(/^(#{1,3})\s+(.+)/);
    if (hm) {
      if (inList) { out.push("</ul>"); inList = false; }
      const level = hm[1].length;
      const tag = `h${level + 2}`; // h3-h5 to keep hierarchy under page h1
      out.push(`<${tag}>${inlineFormat(hm[2])}</${tag}>`);
      continue;
    }

    // list item
    const li = line.match(/^[-*+]\s+(.+)/);
    if (li) {
      if (!inList) { out.push("<ul>"); inList = true; }
      out.push(`<li>${inlineFormat(li[1])}</li>`);
      continue;
    }

    if (inList) { out.push("</ul>"); inList = false; }

    // blank line → paragraph break
    if (!line.trim()) {
      out.push("<br />");
      continue;
    }

    out.push(`<p>${inlineFormat(line)}</p>`);
  }

  if (inList) out.push("</ul>");
  return out.join("\n");
}

function MarkdownAnswer({ content }: { content: string }) {
  return (
    <div
      className="prose-answer text-sm text-zinc-800"
      dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
    />
  );
}

export default function ChatBox() {
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [resp, setResp] = useState<AskResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const answerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (resp) answerRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [resp]);

  async function ask() {
    if (!question.trim()) return;
    setErr(null);
    setBusy(true);
    setResp(null);
    try {
      const out = await apiFetch<AskResponse>("/chat/ask", {
        method: "POST",
        body: JSON.stringify({ question }),
      });
      setResp(out);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Ask failed");
    } finally {
      setBusy(false);
    }
  }

  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) ask();
  }

  return (
    <div className="space-y-4">
      <div className="bg-white border rounded-xl p-4 space-y-3">
        <div className="text-sm font-semibold text-zinc-700">Ask your docs</div>

        <textarea
          className="w-full border rounded-lg px-3 py-2 text-sm min-h-[120px] resize-none focus:outline-none focus:ring-2 focus:ring-zinc-300"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKey}
          placeholder="e.g. What are the top recurring error patterns and what do they usually indicate?"
        />

        <div className="flex items-center gap-3">
          <button
            onClick={ask}
            disabled={busy || !question.trim()}
            className="text-sm px-4 py-2 rounded-lg bg-zinc-900 text-white disabled:opacity-50 hover:bg-zinc-700 transition-colors"
          >
            {busy ? "Thinking…" : "Ask"}
          </button>
          <span className="text-xs text-zinc-400">⌘↵ to submit</span>
          {err && <div className="text-sm text-red-600">{err}</div>}
        </div>
      </div>

      {resp && (
        <div className="space-y-3" ref={answerRef}>
          <div className="bg-white border rounded-xl p-4 space-y-3">
            <div className="text-sm font-semibold text-zinc-700">Answer</div>
            <MarkdownAnswer content={resp.answer_markdown} />
            <FeedbackButtons queryLogId={resp.query_log_id} />
          </div>
          <CitationList citations={resp.citations} />
        </div>
      )}

      <style>{`
        .prose-answer p { margin: 0 0 0.5em; line-height: 1.6; }
        .prose-answer h3, .prose-answer h4, .prose-answer h5 {
          font-weight: 600; margin: 0.75em 0 0.25em;
        }
        .prose-answer h3 { font-size: 1rem; }
        .prose-answer h4 { font-size: 0.9rem; }
        .prose-answer ul { list-style: disc; padding-left: 1.25em; margin: 0.5em 0; }
        .prose-answer li { margin: 0.2em 0; }
        .prose-answer code {
          background: #f4f4f5; border-radius: 3px;
          padding: 0.1em 0.35em; font-size: 0.85em; font-family: monospace;
        }
        .prose-answer strong { font-weight: 600; }
      `}</style>
    </div>
  );
}

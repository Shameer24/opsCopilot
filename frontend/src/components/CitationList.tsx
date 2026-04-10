import type { Citation } from "@/lib/types";

function loc(c: Citation) {
  const parts: string[] = [];
  if (c.page_start != null) parts.push(`pages ${c.page_start}${c.page_end ? `-${c.page_end}` : ""}`);
  if (c.line_start != null) parts.push(`lines ${c.line_start}${c.line_end ? `-${c.line_end}` : ""}`);
  return parts.join(", ");
}

export default function CitationList({ citations }: { citations: Citation[] }) {
  if (!citations || !citations.length) return null;

  return (
    <div className="bg-white border rounded-xl p-4 space-y-2">
      <div className="text-sm font-semibold">Citations</div>
      <ul className="space-y-2">
        {citations.map((c, idx) => (
          <li key={c.chunk_id} className="text-sm">
            <div className="flex items-center justify-between">
              <div className="font-medium">
                [{idx + 1}] {c.filename || "Source"}
              </div>
              <div className="text-xs text-zinc-600">score {c.score.toFixed(3)}</div>
            </div>
            <div className="text-xs text-zinc-600">
              doc {c.document_id} | chunk {c.chunk_id}
              {loc(c) ? ` | ${loc(c)}` : ""}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
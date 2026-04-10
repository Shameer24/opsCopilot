import type { DocumentOut } from "@/lib/types";

function StatusBadge({ status }: { status: string }) {
  const cls =
    status === "READY"
      ? "bg-emerald-100 text-emerald-800"
      : status === "FAILED"
      ? "bg-red-100 text-red-800"
      : status === "PROCESSING"
      ? "bg-amber-100 text-amber-800"
      : "bg-zinc-100 text-zinc-800";

  return <span className={`text-xs px-2 py-1 rounded-full font-medium ${cls}`}>{status}</span>;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface Props {
  docs: DocumentOut[];
  onDelete?: (id: string) => void;
  deleting?: string | null;
}

export default function DocumentTable({ docs, onDelete, deleting }: Props) {
  return (
    <div className="bg-white border rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-zinc-50 border-b">
          <tr>
            <th className="text-left p-3">Filename</th>
            <th className="text-left p-3">Size</th>
            <th className="text-left p-3">Status</th>
            <th className="text-left p-3">Uploaded</th>
            {onDelete && <th className="p-3" />}
          </tr>
        </thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.id} className="border-b last:border-b-0 hover:bg-zinc-50 transition-colors">
              <td className="p-3 font-medium max-w-xs truncate" title={d.filename}>
                {d.filename}
                {d.page_count != null && (
                  <span className="ml-2 text-xs text-zinc-400">{d.page_count}p</span>
                )}
              </td>
              <td className="p-3 text-zinc-500 tabular-nums">{formatBytes(d.file_size_bytes)}</td>
              <td className="p-3">
                <StatusBadge status={d.status} />
              </td>
              <td className="p-3 text-zinc-500">{new Date(d.created_at).toLocaleString()}</td>
              {onDelete && (
                <td className="p-3 text-right">
                  <button
                    onClick={() => onDelete(d.id)}
                    disabled={deleting === d.id}
                    className="text-xs text-red-600 hover:text-red-800 disabled:opacity-40 px-2 py-1 rounded hover:bg-red-50 transition-colors"
                    title="Delete document"
                  >
                    {deleting === d.id ? "Deleting…" : "Delete"}
                  </button>
                </td>
              )}
            </tr>
          ))}
          {docs.length === 0 && (
            <tr>
              <td className="p-6 text-zinc-400 text-center" colSpan={onDelete ? 5 : 4}>
                No documents yet.{" "}
                <a href="/upload" className="text-zinc-600 underline underline-offset-2">
                  Upload one
                </a>
                .
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

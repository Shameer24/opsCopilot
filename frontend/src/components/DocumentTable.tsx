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

  return <span className={`text-xs px-2 py-1 rounded-full ${cls}`}>{status}</span>;
}

export default function DocumentTable({ docs }: { docs: DocumentOut[] }) {
  return (
    <div className="bg-white border rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-zinc-50 border-b">
          <tr>
            <th className="text-left p-3">Filename</th>
            <th className="text-left p-3">Type</th>
            <th className="text-left p-3">Status</th>
            <th className="text-left p-3">Created</th>
          </tr>
        </thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.id} className="border-b last:border-b-0">
              <td className="p-3 font-medium">{d.filename}</td>
              <td className="p-3 text-zinc-600">{d.content_type}</td>
              <td className="p-3">
                <StatusBadge status={d.status} />
              </td>
              <td className="p-3 text-zinc-600">{new Date(d.created_at).toLocaleString()}</td>
            </tr>
          ))}
          {docs.length === 0 ? (
            <tr>
              <td className="p-3 text-zinc-600" colSpan={4}>
                No documents yet.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
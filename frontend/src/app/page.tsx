import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">OpsCopilot</h1>
      <p className="text-zinc-700">
        Upload operational documents and logs, then ask questions with citations.
      </p>
      <div className="flex gap-2">
        <Link href="/upload" className="px-4 py-2 rounded-lg bg-zinc-900 text-white text-sm">
          Upload a document
        </Link>
        <Link href="/chat" className="px-4 py-2 rounded-lg bg-zinc-200 text-sm">
          Open chat
        </Link>
      </div>
    </div>
  );
}
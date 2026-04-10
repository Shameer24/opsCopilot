"use client";

export default function Toast({
  message,
  onClose
}: {
  message: string | null;
  onClose: () => void;
}) {
  if (!message) return null;
  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2">
      <div className="bg-zinc-900 text-white text-sm px-4 py-2 rounded-lg shadow">
        <div className="flex items-center gap-3">
          <div>{message}</div>
          <button className="text-zinc-200 hover:text-white" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
"use client";

import { useRef, useState } from "react";

export default function UploadDropzone({
  onFile
}: {
  onFile: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [drag, setDrag] = useState(false);

  return (
    <div
      className={[
        "border-2 border-dashed rounded-xl p-8 bg-white",
        drag ? "border-zinc-900" : "border-zinc-200"
      ].join(" ")}
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        const f = e.dataTransfer.files?.[0];
        if (f) onFile(f);
      }}
    >
      <div className="space-y-2">
        <div className="font-medium">Drop a file here</div>
        <div className="text-sm text-zinc-600">PDF, TXT, logs. Max size depends on backend config.</div>
        <button
          className="text-sm px-3 py-2 rounded-lg bg-zinc-900 text-white"
          onClick={() => inputRef.current?.click()}
          type="button"
        >
          Choose file
        </button>
      </div>

      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
        }}
      />
    </div>
  );
}
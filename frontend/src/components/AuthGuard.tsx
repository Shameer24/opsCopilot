"use client";

import { useEffect, useState } from "react";
import { ensureSession } from "@/lib/auth";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<"checking" | "ready" | "error">("checking");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function init() {
      try {
        await ensureSession();
        if (!cancelled) setStatus("ready");
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to start session");
          setStatus("error");
        }
      }
    }

    init();
    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "checking") {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-sm text-zinc-600">
        Starting session...
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-sm text-red-600">
        {error || "Unable to start session."}
      </div>
    );
  }

  return <>{children}</>;
}

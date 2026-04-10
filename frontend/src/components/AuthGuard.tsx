"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthed } from "@/lib/auth";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ok, setOk] = useState(false);

  useEffect(() => {
    if (!isAuthed()) {
      router.replace("/login");
      return;
    }
    setOk(true);
  }, [router]);

  if (!ok) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-sm text-zinc-600">
        Checking session...
      </div>
    );
  }

  return <>{children}</>;
}
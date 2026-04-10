"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, getSessionMode, isAuthed, isGuestSession } from "@/lib/auth";

function NavItem({ href, label }: { href: string; label: string }) {
  const pathname = usePathname();
  const active = pathname === href;

  return (
    <Link
      href={href}
      className={active ? "text-zinc-900 font-medium" : "text-zinc-700 hover:text-zinc-900"}
    >
      {label}
    </Link>
  );
}

export default function Navbar() {
  const router = useRouter();
  const authed = isAuthed();
  const sessionMode = getSessionMode();
  const guest = isGuestSession();

  return (
    <header className="border-b bg-white">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="font-semibold">
          OpsCopilot
        </Link>

        {authed ? (
          <nav className="flex items-center gap-2">
            <NavItem href="/documents" label="Documents" />
            <NavItem href="/upload" label="Upload" />
            <NavItem href="/chat" label="Chat" />
            {guest ? (
              <Link
                href="/register"
                className="text-sm px-3 py-2 rounded-lg bg-zinc-900 text-white"
              >
                Save account
              </Link>
            ) : null}
            <button
              onClick={() => {
                clearToken();
                router.replace("/");
              }}
              className="text-sm px-3 py-2 rounded-lg text-zinc-700 hover:bg-zinc-200"
            >
              {sessionMode === "guest" ? "Reset guest" : "Logout"}
            </button>
          </nav>
        ) : (
          <nav className="flex items-center gap-2">
            <Link href="/login" className="text-sm px-3 py-2 rounded-lg hover:bg-zinc-200">
              Login
            </Link>
            <Link href="/register" className="text-sm px-3 py-2 rounded-lg bg-zinc-900 text-white">
              Register
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
}

import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "OpsCopilot",
  description: "AI Knowledge + Operations Assistant"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="max-w-5xl mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
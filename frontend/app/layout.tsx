import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Restaurant AI Agent — System Status",
  description: "Phase 1 Foundation status page for Restaurant AI Agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <header className="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg">
                R
              </div>
              <span className="font-semibold text-slate-900 dark:text-slate-100">
                Restaurant AI Agent
              </span>
            </div>
            <div className="text-xs px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 font-mono">
              Phase 1: Foundation
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-8">
          {children}
        </main>

        <footer className="border-t border-slate-200 dark:border-slate-800 py-6 mt-12 text-center text-xs text-slate-500">
          Restaurant AI Agent &copy; {new Date().getFullYear()} &middot; Phase 1 Foundation Stack
        </footer>
      </body>
    </html>
  );
}

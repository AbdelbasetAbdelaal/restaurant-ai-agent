"use client";

import { useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Next.js App error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] text-center p-6 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm max-w-lg mx-auto">
      <div className="w-12 h-12 rounded-full bg-rose-100 dark:bg-rose-950 flex items-center justify-center mb-4">
        <AlertCircle className="w-6 h-6 text-rose-600 dark:text-rose-400" />
      </div>
      <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
        Failed to load status
      </h2>
      <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 mb-6">
        {error.message || "An unexpected error occurred while communicating with the backend."}
      </p>
      <button
        onClick={() => reset()}
        className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition"
      >
        <RefreshCw className="w-4 h-4" />
        Retry Connection
      </button>
    </div>
  );
}

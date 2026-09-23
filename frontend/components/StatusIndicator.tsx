import React from "react";
import { CheckCircle2, XCircle, RefreshCw } from "lucide-react";

interface StatusIndicatorProps {
  name: string;
  status: "Connected" | "Offline" | "Loading";
  message?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  name,
  status,
  message,
}) => {
  const isConnected = status === "Connected";
  const isLoading = status === "Loading";

  return (
    <div className="flex items-center justify-between p-4 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm transition-all">
      <div className="flex flex-col">
        <span className="text-base font-semibold text-slate-900 dark:text-slate-100">
          {name}
        </span>
        {message && (
          <span className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            {message}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        {isLoading ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            Connecting...
          </span>
        ) : isConnected ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            Connected
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
            <XCircle className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" />
            Offline
          </span>
        )}
      </div>
    </div>
  );
};

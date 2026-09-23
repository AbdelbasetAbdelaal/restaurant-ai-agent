"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient, SystemHealthResponse } from "@/lib/api-client";
import { StatusIndicator } from "@/components/StatusIndicator";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { RefreshCw, Activity, Server, Clock } from "lucide-react";

export default function StatusPage() {
  const [healthData, setHealthData] = useState<SystemHealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isBackendOffline, setIsBackendOffline] = useState<boolean>(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const fetchStatus = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getHealth();
      setHealthData(data);
      setIsBackendOffline(false);
    } catch {
      // Backend is unreachable
      setIsBackendOffline(true);
      setHealthData(null);
    } finally {
      setIsLoading(false);
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    // Auto-poll health status every 15 seconds
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  // Derived statuses
  const backendStatus: "Connected" | "Offline" | "Loading" = isLoading && !lastChecked
    ? "Loading"
    : isBackendOffline
    ? "Offline"
    : "Connected";

  const databaseStatus: "Connected" | "Offline" | "Loading" = isLoading && !lastChecked
    ? "Loading"
    : isBackendOffline || !healthData
    ? "Offline"
    : healthData.components.database.status;

  const redisStatus: "Connected" | "Offline" | "Loading" = isLoading && !lastChecked
    ? "Loading"
    : isBackendOffline || !healthData
    ? "Offline"
    : healthData.components.redis.status;

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        {/* Title & Introduction */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Server className="w-6 h-6 text-indigo-600" />
              Restaurant AI Agent
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Phase 1: Foundation Infrastructure Verification
            </p>
          </div>

          <button
            onClick={fetchStatus}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-750 transition shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh Status
          </button>
        </div>

        {/* System Status Container */}
        <div className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-500" />
              System Status
            </h2>
            {isBackendOffline ? (
              <span className="text-xs px-2.5 py-0.5 rounded-full font-medium uppercase tracking-wider bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">
                Offline
              </span>
            ) : healthData ? (
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium uppercase tracking-wider ${
                healthData.status === "ok"
                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                  : "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
              }`}>
                {healthData.status}
              </span>
            ) : null}
          </div>

          {/* Core Subsystem Indicators */}
          <div className="grid gap-3 sm:grid-cols-1">
            <StatusIndicator
              name="Backend"
              status={backendStatus}
              message={
                isBackendOffline
                  ? "Unable to reach FastAPI backend service."
                  : healthData?.components.backend.message || "FastAPI operational"
              }
            />

            <StatusIndicator
              name="Database"
              status={databaseStatus}
              message={
                isBackendOffline
                  ? "Status unavailable (Backend offline)"
                  : healthData?.components.database.message || "PostgreSQL connection active"
              }
            />

            <StatusIndicator
              name="Redis"
              status={redisStatus}
              message={
                isBackendOffline
                  ? "Status unavailable (Backend offline)"
                  : healthData?.components.redis.message || "Redis cache/queue connection active"
              }
            />
          </div>
        </div>

        {/* System Metadata Card */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm text-xs text-slate-500 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" />
            <span>
              Last Checked:{" "}
              {lastChecked ? lastChecked.toLocaleTimeString() : "Never"}
            </span>
          </div>

          <div className="flex items-center gap-4">
            <span>Environment: <strong>{healthData?.environment || "Unknown"}</strong></span>
            <span>Version: <strong>{healthData?.version || "0.1.0"}</strong></span>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}

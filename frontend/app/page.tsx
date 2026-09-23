"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  apiClient,
  SystemHealthResponse,
  Restaurant,
  RestaurantSettings,
  Customer,
  Staff,
} from "@/lib/api-client";
import { StatusIndicator } from "@/components/StatusIndicator";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import {
  RefreshCw,
  Activity,
  Server,
  Clock,
  Building2,
  Users,
  UserCheck,
  Sliders,
  AlertTriangle,
  Globe,
  DollarSign,
  Phone,
  Mail,
  MapPin,
  CheckCircle,
  XCircle,
} from "lucide-react";

export default function StatusPage() {
  const [healthData, setHealthData] = useState<SystemHealthResponse | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState<boolean>(true);
  const [isBackendOffline, setIsBackendOffline] = useState<boolean>(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  // Phase 2 State
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);
  const [settings, setSettings] = useState<RestaurantSettings | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [staffList, setStaffList] = useState<Staff[]>([]);
  const [isLoadingFoundation, setIsLoadingFoundation] = useState<boolean>(false);
  const [foundationError, setFoundationError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    setIsLoadingHealth(true);
    try {
      const data = await apiClient.getHealth();
      setHealthData(data);
      setIsBackendOffline(false);
      return data;
    } catch {
      setIsBackendOffline(true);
      setHealthData(null);
      return null;
    } finally {
      setIsLoadingHealth(false);
      setLastChecked(new Date());
    }
  }, []);

  const fetchRestaurantDetails = useCallback(async (restaurantId: string) => {
    try {
      const [settingsRes, customersRes, staffRes] = await Promise.allSettled([
        apiClient.restaurants.getSettings(restaurantId),
        apiClient.customers.list(restaurantId, 0, 10),
        apiClient.staff.list(restaurantId, 0, 10),
      ]);

      if (settingsRes.status === "fulfilled") {
        setSettings(settingsRes.value);
      } else {
        setSettings(null);
      }

      if (customersRes.status === "fulfilled") {
        setCustomers(customersRes.value);
      } else {
        setCustomers([]);
      }

      if (staffRes.status === "fulfilled") {
        setStaffList(staffRes.value);
      } else {
        setStaffList([]);
      }
    } catch (err: unknown) {
      console.error("Failed to load restaurant details:", err);
    }
  }, []);

  const fetchFoundationData = useCallback(async () => {
    setIsLoadingFoundation(true);
    setFoundationError(null);

    try {
      const list = await apiClient.restaurants.list(0, 50);
      setRestaurants(list);
      if (list.length > 0) {
        const active = list[0];
        setSelectedRestaurant(active);
        await fetchRestaurantDetails(active.id);
      } else {
        setSelectedRestaurant(null);
        setSettings(null);
        setCustomers([]);
        setStaffList([]);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Database unavailable or offline";
      setFoundationError(msg);
      setRestaurants([]);
      setSelectedRestaurant(null);
    } finally {
      setIsLoadingFoundation(false);
    }
  }, [fetchRestaurantDetails]);

  const refreshAll = useCallback(async () => {
    const health = await fetchHealth();
    if (health?.components.database.status === "Connected") {
      await fetchFoundationData();
    } else {
      setFoundationError("Database is offline or not reachable from backend.");
      setRestaurants([]);
      setSelectedRestaurant(null);
    }
  }, [fetchHealth, fetchFoundationData]);

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 20000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  const handleSelectRestaurant = (restaurant: Restaurant) => {
    setSelectedRestaurant(restaurant);
    fetchRestaurantDetails(restaurant.id);
  };

  // Derived statuses
  const backendStatus: "Connected" | "Offline" | "Loading" =
    isLoadingHealth && !lastChecked
      ? "Loading"
      : isBackendOffline
      ? "Offline"
      : "Connected";

  const databaseStatus: "Connected" | "Offline" | "Loading" =
    isLoadingHealth && !lastChecked
      ? "Loading"
      : isBackendOffline || !healthData
      ? "Offline"
      : healthData.components.database.status;

  const redisStatus: "Connected" | "Offline" | "Loading" =
    isLoadingHealth && !lastChecked
      ? "Loading"
      : isBackendOffline || !healthData
      ? "Offline"
      : healthData.components.redis.status;

  return (
    <ErrorBoundary>
      <div className="space-y-8 max-w-6xl mx-auto py-6 px-4">
        {/* Title & Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Server className="w-6 h-6 text-indigo-600" />
              Restaurant AI Agent
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Phase 2: Database & Restaurant Multi-Tenant Foundation
            </p>
          </div>

          <button
            onClick={refreshAll}
            disabled={isLoadingHealth || isLoadingFoundation}
            className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-750 transition shadow-sm disabled:opacity-50"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${
                isLoadingHealth || isLoadingFoundation ? "animate-spin" : ""
              }`}
            />
            Refresh Data
          </button>
        </div>

        {/* Phase 1: Core Subsystem Indicators */}
        <div className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-500" />
              Subsystem Health
            </h2>
            {isBackendOffline ? (
              <span className="text-xs px-2.5 py-0.5 rounded-full font-medium uppercase tracking-wider bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">
                Offline
              </span>
            ) : healthData ? (
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-medium uppercase tracking-wider ${
                  healthData.status === "ok"
                    ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                    : "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                }`}
              >
                {healthData.status}
              </span>
            ) : null}
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
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
                  : healthData?.components.redis.message || "Redis connection active"
              }
            />
          </div>
        </div>

        {/* Phase 2: Restaurant Foundation View */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Building2 className="w-5 h-5 text-indigo-600" />
              Tenant Foundation
            </h2>
            {restaurants.length > 1 && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-500">Switch Restaurant:</span>
                <select
                  value={selectedRestaurant?.id || ""}
                  onChange={(e) => {
                    const r = restaurants.find((x) => x.id === e.target.value);
                    if (r) handleSelectRestaurant(r);
                  }}
                  className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1 text-slate-800 dark:text-slate-200"
                >
                  {restaurants.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name} ({r.slug})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Database Offline or Error Notice */}
          {databaseStatus === "Offline" || foundationError ? (
            <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-2xl p-6 text-amber-900 dark:text-amber-200">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h3 className="font-semibold text-base">
                    Database Offline / Foundation Data Unavailable
                  </h3>
                  <p className="text-sm text-amber-800 dark:text-amber-300">
                    {foundationError ||
                      "PostgreSQL is offline or unreachable. The application handles this gracefully without crashing."}
                  </p>
                  <p className="text-xs text-amber-700 dark:text-amber-400 mt-2">
                    To populate and view tenants, start PostgreSQL, run migrations (
                    <code className="bg-amber-100 dark:bg-amber-900/60 px-1 py-0.5 rounded font-mono">
                      alembic upgrade head
                    </code>
                    ), and optionally run development seed (
                    <code className="bg-amber-100 dark:bg-amber-900/60 px-1 py-0.5 rounded font-mono">
                      python -m app.db.seed
                    </code>
                    ).
                  </p>
                </div>
              </div>
            </div>
          ) : !selectedRestaurant ? (
            <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-8 text-center text-slate-500">
              <Building2 className="w-12 h-12 mx-auto mb-3 text-slate-400" />
              <h3 className="text-base font-semibold text-slate-800 dark:text-slate-200">
                No Restaurants Found
              </h3>
              <p className="text-sm mt-1">
                The database is connected, but no restaurant tenants have been created yet.
              </p>
              <p className="text-xs text-slate-400 mt-2">
                Run{" "}
                <code className="bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded font-mono">
                  python -m app.db.seed
                </code>{" "}
                in the backend to create the default demonstration tenant.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Restaurant Details & Settings Card */}
              <div className="lg:col-span-2 space-y-6">
                {/* Identity Card */}
                <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">
                        {selectedRestaurant.name}
                      </h3>
                      <p className="text-xs text-slate-400 font-mono mt-0.5">
                        slug: /{selectedRestaurant.slug} • id: {selectedRestaurant.id}
                      </p>
                    </div>
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        selectedRestaurant.is_active
                          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                          : "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300"
                      }`}
                    >
                      {selectedRestaurant.is_active ? (
                        <>
                          <CheckCircle className="w-3 h-3" /> Active
                        </>
                      ) : (
                        <>
                          <XCircle className="w-3 h-3" /> Inactive
                        </>
                      )}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2 border-t border-slate-100 dark:border-slate-700 text-xs">
                    <div>
                      <span className="text-slate-400 block flex items-center gap-1">
                        <DollarSign className="w-3.5 h-3.5" /> Currency
                      </span>
                      <span className="font-semibold text-slate-700 dark:text-slate-200 text-sm">
                        {selectedRestaurant.currency}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 block flex items-center gap-1">
                        <Globe className="w-3.5 h-3.5" /> Timezone
                      </span>
                      <span className="font-semibold text-slate-700 dark:text-slate-200 text-sm">
                        {selectedRestaurant.timezone}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 block flex items-center gap-1">
                        <Phone className="w-3.5 h-3.5" /> Contact Phone
                      </span>
                      <span className="font-semibold text-slate-700 dark:text-slate-200 text-sm truncate block">
                        {selectedRestaurant.phone || "—"}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 block flex items-center gap-1">
                        <Mail className="w-3.5 h-3.5" /> Contact Email
                      </span>
                      <span className="font-semibold text-slate-700 dark:text-slate-200 text-sm truncate block">
                        {selectedRestaurant.email || "—"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Settings Card */}
                {settings && (
                  <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                        <Sliders className="w-4 h-4 text-indigo-500" />
                        Operational Settings
                      </h4>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          settings.is_accepting_orders
                            ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300"
                            : "bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300"
                        }`}
                      >
                        {settings.is_accepting_orders ? "Accepting Orders" : "Orders Paused"}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                      <div>
                        <span className="text-slate-400">Display Name:</span>
                        <p className="font-medium text-slate-700 dark:text-slate-300">
                          {settings.display_name}
                        </p>
                      </div>

                      <div>
                        <span className="text-slate-400">Location:</span>
                        <p className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-slate-400" />
                          {[settings.city, settings.country].filter(Boolean).join(", ") || "—"}
                        </p>
                      </div>

                      {settings.address && (
                        <div className="sm:col-span-2">
                          <span className="text-slate-400">Street Address:</span>
                          <p className="font-medium text-slate-700 dark:text-slate-300">
                            {settings.address}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Customers & Staff Sidebar */}
              <div className="space-y-6">
                {/* Staff Summary */}
                <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                      <UserCheck className="w-4 h-4 text-indigo-500" />
                      Staff Members
                    </h4>
                    <span className="text-xs bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded-full font-medium">
                      {staffList.length}
                    </span>
                  </div>

                  {staffList.length === 0 ? (
                    <p className="text-xs text-slate-400">No staff registered for this tenant.</p>
                  ) : (
                    <div className="space-y-2">
                      {staffList.map((member) => (
                        <div
                          key={member.id}
                          className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-50 dark:bg-slate-750"
                        >
                          <div>
                            <p className="font-semibold text-slate-800 dark:text-slate-200">
                              {member.name}
                            </p>
                            <p className="text-slate-400">{member.email}</p>
                          </div>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-medium">
                            {member.role}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Customers Summary */}
                <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                      <Users className="w-4 h-4 text-indigo-500" />
                      Customers
                    </h4>
                    <span className="text-xs bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded-full font-medium">
                      {customers.length}
                    </span>
                  </div>

                  {customers.length === 0 ? (
                    <p className="text-xs text-slate-400">No customers registered yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {customers.map((cust) => (
                        <div
                          key={cust.id}
                          className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-50 dark:bg-slate-750"
                        >
                          <div>
                            <p className="font-semibold text-slate-800 dark:text-slate-200">
                              {cust.name}
                            </p>
                            <p className="text-slate-400 font-mono">{cust.phone || "No phone"}</p>
                          </div>
                          {cust.notes && (
                            <span className="text-[10px] text-slate-400 truncate max-w-[100px]">
                              {cust.notes}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* System Metadata Card */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm text-xs text-slate-500 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" />
            <span>
              Last Checked: {lastChecked ? lastChecked.toLocaleTimeString() : "Never"}
            </span>
          </div>

          <div className="flex items-center gap-4">
            <span>
              Environment: <strong>{healthData?.environment || "development"}</strong>
            </span>
            <span>
              Version: <strong>0.2.0 (Phase 2 Foundation)</strong>
            </span>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}

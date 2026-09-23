import { config } from "./config";

export interface ComponentHealth {
  status: "Connected" | "Offline";
  message?: string;
}

export interface SystemHealthResponse {
  status: "ok" | "degraded" | "down";
  service: string;
  environment: string;
  version: string;
  timestamp: string;
  components: {
    backend: ComponentHealth;
    database: ComponentHealth;
    redis: ComponentHealth;
  };
}

export interface ApiError {
  code: string;
  message: string;
  request_id?: string;
  details?: unknown[];
}

export class ApiClientError extends Error {
  public code: string;
  public status: number;
  public requestId?: string;
  public details?: unknown[];

  constructor(message: string, status: number, errorData?: ApiError) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = errorData?.code || "CLIENT_ERROR";
    this.requestId = errorData?.request_id;
    this.details = errorData?.details;
  }
}

// ----------------------------------------------------------------------------
// Phase 2 Domain Types
// ----------------------------------------------------------------------------

export interface Restaurant {
  id: string;
  name: string;
  slug: string;
  phone?: string | null;
  email?: string | null;
  currency: string;
  timezone: string;
  whatsapp_phone_number_id?: string | null;
  whatsapp_business_account_id?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RestaurantCreate {
  name: string;
  slug?: string;
  phone?: string;
  email?: string;
  currency?: string;
  timezone?: string;
  whatsapp_phone_number_id?: string;
  whatsapp_business_account_id?: string;
}

export interface RestaurantUpdate {
  name?: string;
  phone?: string;
  email?: string;
  currency?: string;
  timezone?: string;
  whatsapp_phone_number_id?: string;
  whatsapp_business_account_id?: string;
  is_active?: boolean;
}

export interface RestaurantSettings {
  id: string;
  restaurant_id: string;
  display_name: string;
  description?: string | null;
  default_currency: string;
  timezone: string;
  contact_phone?: string | null;
  contact_email?: string | null;
  address?: string | null;
  city?: string | null;
  country: string;
  is_accepting_orders: boolean;
  created_at: string;
  updated_at: string;
}

export interface RestaurantSettingsUpdate {
  display_name?: string;
  description?: string;
  default_currency?: string;
  timezone?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  city?: string;
  country?: string;
  is_accepting_orders?: boolean;
}

export interface Customer {
  id: string;
  restaurant_id: string;
  name: string;
  phone: string;
  email?: string | null;
  notes?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CustomerCreate {
  name: string;
  phone: string;
  email?: string;
  notes?: string;
}

export interface CustomerUpdate {
  name?: string;
  phone?: string;
  email?: string;
  notes?: string;
  is_active?: boolean;
}

export type StaffRole = "OWNER" | "MANAGER" | "STAFF";

export interface Staff {
  id: string;
  restaurant_id: string;
  name: string;
  email: string;
  phone?: string | null;
  role: StaffRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface StaffCreate {
  name: string;
  email: string;
  role: StaffRole;
  phone?: string;
}

export interface StaffUpdate {
  name?: string;
  email?: string;
  role?: StaffRole;
  phone?: string;
  is_active?: boolean;
}

/**
 * Reusable HTTP Client wrapping fetch with error handling, correlation headers,
 * and JSON decoding.
 */
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
    const headers = new Headers(options.headers || {});

    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        cache: "no-store",
      });

      if (!response.ok) {
        let errorData: { error?: ApiError } = {};
        try {
          errorData = await response.json();
        } catch {
          // Response body was not JSON
        }
        throw new ApiClientError(
          errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData.error
        );
      }

      return (await response.json()) as T;
    } catch (err: unknown) {
      if (err instanceof ApiClientError) {
        throw err;
      }
      throw new ApiClientError(
        err instanceof Error ? err.message : "Network error occurred",
        0
      );
    }
  }

  // --------------------------------------------------------------------------
  // Health Check APIs
  // --------------------------------------------------------------------------

  public async getHealth(): Promise<SystemHealthResponse> {
    return this.request<SystemHealthResponse>("/api/v1/health");
  }

  // --------------------------------------------------------------------------
  // Phase 2: Restaurant Foundation APIs
  // --------------------------------------------------------------------------

  public readonly restaurants = {
    list: async (skip: number = 0, limit: number = 100): Promise<Restaurant[]> => {
      return this.request<Restaurant[]>(`/api/v1/restaurants?skip=${skip}&limit=${limit}`);
    },
    get: async (id: string): Promise<Restaurant> => {
      return this.request<Restaurant>(`/api/v1/restaurants/${id}`);
    },
    create: async (data: RestaurantCreate): Promise<Restaurant> => {
      return this.request<Restaurant>("/api/v1/restaurants", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },
    update: async (id: string, data: RestaurantUpdate): Promise<Restaurant> => {
      return this.request<Restaurant>(`/api/v1/restaurants/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      });
    },
    getSettings: async (id: string): Promise<RestaurantSettings> => {
      return this.request<RestaurantSettings>(`/api/v1/restaurants/${id}/settings`);
    },
    updateSettings: async (
      id: string,
      data: RestaurantSettingsUpdate
    ): Promise<RestaurantSettings> => {
      return this.request<RestaurantSettings>(`/api/v1/restaurants/${id}/settings`, {
        method: "PATCH",
        body: JSON.stringify(data),
      });
    },
  };

  public readonly customers = {
    list: async (
      restaurantId: string,
      skip: number = 0,
      limit: number = 100
    ): Promise<Customer[]> => {
      return this.request<Customer[]>(
        `/api/v1/restaurants/${restaurantId}/customers?skip=${skip}&limit=${limit}`
      );
    },
    get: async (restaurantId: string, customerId: string): Promise<Customer> => {
      return this.request<Customer>(
        `/api/v1/restaurants/${restaurantId}/customers/${customerId}`
      );
    },
    create: async (restaurantId: string, data: CustomerCreate): Promise<Customer> => {
      return this.request<Customer>(`/api/v1/restaurants/${restaurantId}/customers`, {
        method: "POST",
        body: JSON.stringify(data),
      });
    },
    update: async (
      restaurantId: string,
      customerId: string,
      data: CustomerUpdate
    ): Promise<Customer> => {
      return this.request<Customer>(
        `/api/v1/restaurants/${restaurantId}/customers/${customerId}`,
        {
          method: "PATCH",
          body: JSON.stringify(data),
        }
      );
    },
  };

  public readonly staff = {
    list: async (
      restaurantId: string,
      skip: number = 0,
      limit: number = 100
    ): Promise<Staff[]> => {
      return this.request<Staff[]>(
        `/api/v1/restaurants/${restaurantId}/staff?skip=${skip}&limit=${limit}`
      );
    },
    get: async (restaurantId: string, staffId: string): Promise<Staff> => {
      return this.request<Staff>(
        `/api/v1/restaurants/${restaurantId}/staff/${staffId}`
      );
    },
    create: async (restaurantId: string, data: StaffCreate): Promise<Staff> => {
      return this.request<Staff>(`/api/v1/restaurants/${restaurantId}/staff`, {
        method: "POST",
        body: JSON.stringify(data),
      });
    },
    update: async (
      restaurantId: string,
      staffId: string,
      data: StaffUpdate
    ): Promise<Staff> => {
      return this.request<Staff>(
        `/api/v1/restaurants/${restaurantId}/staff/${staffId}`,
        {
          method: "PATCH",
          body: JSON.stringify(data),
        }
      );
    },
  };
}

// Export singleton API client
export const apiClient = new ApiClient(config.apiBaseUrl);

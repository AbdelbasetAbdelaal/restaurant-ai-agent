/**
 * Centralized frontend application configuration.
 */
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  appName: "Restaurant AI Agent",
  environment: process.env.NODE_ENV || "development",
};

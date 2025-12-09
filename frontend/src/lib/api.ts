/**
 * API Configuration
 *
 * Centralized API configuration for the frontend application.
 * Uses environment variables with fallback to localhost for development.
 */

// API base URL - reads from environment variable or defaults to localhost
export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Helper function to build API URLs
 * @param path - API path (should start with /)
 * @returns Full API URL
 */
export function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

/**
 * Standard fetch wrapper with error handling
 * @param path - API path
 * @param options - Fetch options
 * @returns Response data
 */
export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText}`);
  }

  return response.json();
}

/**
 * GET request helper
 */
export async function apiGet<T>(path: string): Promise<T> {
  return apiFetch<T>(path, { method: "GET" });
}

/**
 * POST request helper
 */
export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

/**
 * DELETE request helper
 */
export async function apiDelete<T>(path: string): Promise<T> {
  return apiFetch<T>(path, { method: "DELETE" });
}

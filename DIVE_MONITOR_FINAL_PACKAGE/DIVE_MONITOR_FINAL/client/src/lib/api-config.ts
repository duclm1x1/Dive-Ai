/**
 * API Configuration with Backend Detection
 * 
 * Handles environment-aware API URLs and backend availability detection
 */

const DEFAULT_BACKEND_URL = 'http://localhost:8787';

/**
 * Get the backend API URL based on environment
 */
export function getBackendUrl(): string {
  // In development, use localhost
  if (import.meta.env.DEV) {
    return DEFAULT_BACKEND_URL;
  }
  
  // In production, backend is not available (web-static project)
  // Return empty string to indicate no backend
  return '';
}

/**
 * Check if backend is available
 */
export async function isBackendAvailable(): Promise<boolean> {
  const backendUrl = getBackendUrl();
  
  if (!backendUrl) {
    return false;
  }
  
  try {
    const response = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(2000), // 2 second timeout
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Safe fetch with backend detection
 */
export async function safeFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<{ data: T | null; error: string | null; isBackendAvailable: boolean }> {
  const backendUrl = getBackendUrl();
  
  if (!backendUrl) {
    return {
      data: null,
      error: 'Backend not available in this environment',
      isBackendAvailable: false,
    };
  }
  
  try {
    const response = await fetch(`${backendUrl}${endpoint}`, {
      ...options,
      signal: options?.signal || AbortSignal.timeout(10000), // 10 second default timeout
    });
    
    if (!response.ok) {
      return {
        data: null,
        error: `HTTP ${response.status}: ${response.statusText}`,
        isBackendAvailable: true,
      };
    }
    
    const data = await response.json();
    return {
      data,
      error: null,
      isBackendAvailable: true,
    };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      isBackendAvailable: false,
    };
  }
}

/**
 * Build full API URL
 */
export function buildApiUrl(endpoint: string): string {
  const backendUrl = getBackendUrl();
  return backendUrl ? `${backendUrl}${endpoint}` : '';
}

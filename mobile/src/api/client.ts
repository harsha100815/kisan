/**
 * Typed API client skeleton. No calls are made in Phase 0 screens; this file
 * establishes base-URL handling and a typed get() so later phases plug in.
 */
const DEFAULT_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000/api/v1';

let baseUrl = DEFAULT_URL;

export function setApiBaseUrl(url: string): void {
  baseUrl = url.replace(/\/$/, '');
}

export function getApiBaseUrl(): string {
  return baseUrl;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${baseUrl}${path}`, {
    headers: { Accept: 'application/json', ...init?.headers },
    ...init,
  });
  if (!resp.ok) throw new ApiError(resp.status, `API ${resp.status} on ${path}`);
  return (await resp.json()) as T;
}

export interface HealthStatus {
  status: string;
  env: string;
  version: string;
}

export interface PriceRow {
  market: string;
  district: string;
  state: string;
  commodity: string;
  variety: string | null;
  observation_date: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  source: string;
}

export interface PricesToday {
  source: string;
  date: string;
  count: number;
  rows: PriceRow[];
}

export const api = {
  health: () => request<HealthStatus>('/health'),
  pricesToday: (params?: { commodity?: string; state?: string }) => {
    const query = params?.commodity
      ? `?commodity=${encodeURIComponent(params.commodity)}`
      : params?.state
        ? `?state=${encodeURIComponent(params.state)}`
        : '';
    return request<PricesToday>(`/prices/today${query}`);
  },
};

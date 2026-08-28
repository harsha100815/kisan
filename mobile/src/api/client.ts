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

export interface DiagnosisResult {
  audit_id: string;
  status: 'completed' | 'unavailable' | 'failed';
  is_definitive: boolean;
  confidence_band: 'high' | 'medium' | 'low' | null;
  prediction: { disease_key: string; confidence: number } | null;
  alternatives: { disease_key: string; confidence: number }[];
  provider: string;
  model_version: string | null;
  disclaimer_key: string;
}

async function requestForm<T>(path: string, form: FormData): Promise<T> {
  const resp = await fetch(`${baseUrl}${path}`, { method: 'POST', body: form });
  if (!resp.ok) throw new ApiError(resp.status, `API ${resp.status} on ${path}`);
  return (await resp.json()) as T;
}

export const api = {
  health: () => request<HealthStatus>('/health'),
  diagnose: (imageUri: string, cropKey?: string, language = 'hi') => {
    const form = new FormData();
    const name = imageUri.split('/').pop() ?? 'photo.jpg';
    const ext = name.includes('.') ? name.split('.').pop()!.toLowerCase() : 'jpg';
    const mime = ext === 'png' ? 'image/png' : 'image/jpeg';
    form.append('image', { uri: imageUri, name, type: mime } as unknown as Blob);
    if (cropKey) form.append('crop_key', cropKey);
    form.append('language', language);
    return requestForm<DiagnosisResult>('/diagnosis/diagnose', form);
  },
  pricesToday: (params?: { commodity?: string; state?: string }) => {
    const query = params?.commodity
      ? `?commodity=${encodeURIComponent(params.commodity)}`
      : params?.state
        ? `?state=${encodeURIComponent(params.state)}`
        : '';
    return request<PricesToday>(`/prices/today${query}`);
  },
};

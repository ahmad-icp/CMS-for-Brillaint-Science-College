export interface LoginInput {
  college_id: string;
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

const ACCESS_KEY = 'college-erp.access-token';
const REFRESH_KEY = 'college-erp.refresh-token';
const PROFILE_KEY = 'college-erp.profile';
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}

export function getStoredProfile(): Pick<LoginInput, 'college_id' | 'username'> | null {
  const raw = localStorage.getItem(PROFILE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function storeTokens(tokens: TokenResponse) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

export function clearSession() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(PROFILE_KEY);
  window.dispatchEvent(new Event('college-erp:session-expired'));
}

export async function login(input: LoginInput): Promise<void> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unable to sign in' }));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Unable to sign in');
  }
  storeTokens(await response.json());
  localStorage.setItem(PROFILE_KEY, JSON.stringify({ college_id: input.college_id, username: input.username }));
}

async function refreshWith(nativeFetch: typeof window.fetch): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;
  const response = await nativeFetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) {
    clearSession();
    return null;
  }
  const tokens: TokenResponse = await response.json();
  storeTokens(tokens);
  return tokens.access_token;
}

export async function logout(): Promise<void> {
  const refreshToken = getRefreshToken();
  if (refreshToken) {
    await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    }).catch(() => undefined);
  }
  clearSession();
}

export function installAuthenticatedFetch() {
  const nativeFetch = window.fetch.bind(window);
  window.fetch = async (input: RequestInfo | URL, init: RequestInit = {}) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
    const isApiRequest = url.startsWith('/api/') || url.startsWith(API_BASE) || url.startsWith(window.location.origin + '/api/');
    const isAuthRequest = url.includes('/auth/login') || url.includes('/auth/refresh');
    const headers = new Headers(init.headers);
    headers.delete('X-Role');
    if (isApiRequest && !isAuthRequest) {
      const token = getAccessToken();
      if (token) headers.set('Authorization', `Bearer ${token}`);
    }

    let response = await nativeFetch(input, { ...init, headers });
    if (response.status === 401 && isApiRequest && !isAuthRequest && getRefreshToken()) {
      const token = await refreshWith(nativeFetch);
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
        response = await nativeFetch(input, { ...init, headers });
      }
    }
    return response;
  };
}

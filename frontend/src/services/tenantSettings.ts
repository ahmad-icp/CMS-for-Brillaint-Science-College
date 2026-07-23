export interface TenantSettings {
  institution_name: string;
  campus_name: string;
  principal_name: string;
  address: string;
  phone: string;
  email: string;
  website: string;
  academic_year: string;
  timezone: string;
  currency: string;
  logo_url: string;
  primary_color: string;
  college_id?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export async function loadTenantSettings(): Promise<TenantSettings | null> {
  const response = await fetch(`${API_BASE}/tenant-settings/me`);
  if (response.status === 404) return null;
  if (!response.ok) throw new Error('Unable to load institution settings');
  return response.json();
}

export async function saveTenantSettings(settings: TenantSettings): Promise<TenantSettings> {
  const response = await fetch(`${API_BASE}/tenant-settings/me`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unable to save institution settings' }));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Unable to save institution settings');
  }
  return response.json();
}

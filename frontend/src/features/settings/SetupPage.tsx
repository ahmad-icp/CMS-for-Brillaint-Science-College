import { FormEvent, useEffect, useState } from 'react';

import { loadTenantSettings, saveTenantSettings, TenantSettings } from '../../services/tenantSettings';

const defaults: TenantSettings = {
  institution_name: 'Brilliant Science College',
  campus_name: 'Main Campus',
  principal_name: '',
  address: '',
  phone: '',
  email: '',
  website: '',
  academic_year: '2026-2027',
  timezone: 'Asia/Karachi',
  currency: 'PKR',
  logo_url: '',
  primary_color: '#1F4E79',
};

export function SetupPage() {
  const [form, setForm] = useState<TenantSettings>(defaults);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadTenantSettings()
      .then((saved) => { if (saved) setForm(saved); })
      .catch((error) => setMessage(error instanceof Error ? error.message : 'Unable to load settings'))
      .finally(() => setLoading(false));
  }, []);

  function field<K extends keyof TenantSettings>(name: K, value: TenantSettings[K]) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      setForm(await saveTenantSettings(form));
      setMessage('Institution profile saved successfully.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to save settings');
    } finally {
      setSaving(false);
    }
  }

  return (
    <section>
      <div className="page-intro">
        <div><p className="eyebrow">Step 1 of ERP setup</p><h2>Institution profile</h2>
          <p>These details are stored in PostgreSQL and identify this college across the ERP.</p></div>
        <span className="status-badge">{loading ? 'Loading…' : 'Ready'}</span>
      </div>
      <form className="panel setup-form" onSubmit={submit}>
        <div className="section-heading"><h3>Identity and leadership</h3><p>Use the official information shown on college documents.</p></div>
        <div className="form-grid">
          <label>Institution name<input required minLength={2} value={form.institution_name} onChange={(e) => field('institution_name', e.target.value)} /></label>
          <label>Campus name<input value={form.campus_name} onChange={(e) => field('campus_name', e.target.value)} /></label>
          <label>Principal name<input value={form.principal_name} onChange={(e) => field('principal_name', e.target.value)} /></label>
          <label>Academic year<input placeholder="2026-2027" value={form.academic_year} onChange={(e) => field('academic_year', e.target.value)} /></label>
        </div>
        <div className="section-heading"><h3>Contact details</h3></div>
        <div className="form-grid">
          <label className="wide">Address<textarea rows={3} value={form.address} onChange={(e) => field('address', e.target.value)} /></label>
          <label>Phone<input type="tel" value={form.phone} onChange={(e) => field('phone', e.target.value)} /></label>
          <label>Email<input type="email" value={form.email} onChange={(e) => field('email', e.target.value)} /></label>
          <label>Website<input type="url" placeholder="https://" value={form.website} onChange={(e) => field('website', e.target.value)} /></label>
        </div>
        <div className="section-heading"><h3>Regional and visual settings</h3></div>
        <div className="form-grid">
          <label>Timezone<input value={form.timezone} onChange={(e) => field('timezone', e.target.value)} /></label>
          <label>Currency<input minLength={3} maxLength={8} value={form.currency} onChange={(e) => field('currency', e.target.value.toUpperCase())} /></label>
          <label>Logo URL<input type="url" placeholder="https://" value={form.logo_url} onChange={(e) => field('logo_url', e.target.value)} /></label>
          <label>Brand colour<input type="color" value={form.primary_color} onChange={(e) => field('primary_color', e.target.value)} /></label>
        </div>
        {message && <p className={message.includes('successfully') ? 'success-message' : 'alert'} role="status">{message}</p>}
        <div className="form-actions"><button className="primary-button" disabled={loading || saving}>{saving ? 'Saving…' : 'Save institution profile'}</button></div>
      </form>
    </section>
  );
}

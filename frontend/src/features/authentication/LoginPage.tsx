import { FormEvent, useState } from 'react';

import { useAuth } from '../../auth/AuthContext';

export function LoginPage() {
  const { login } = useAuth();
  const [form, setForm] = useState({ college_id: 'college-001', username: 'admin', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to sign in');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-card">
        <div className="brand-mark">BSC</div>
        <p className="eyebrow">Secure college administration</p>
        <h1>College ERP</h1>
        <p className="muted">Sign in to manage academics, students, examinations and finance.</p>
        <form onSubmit={submit} className="form-stack">
          <label>College ID<input required value={form.college_id} onChange={(e) => setForm({ ...form, college_id: e.target.value })} /></label>
          <label>Username or email<input required autoComplete="username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
          <label>Password<input required type="password" autoComplete="current-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          {error && <p className="alert" role="alert">{error}</p>}
          <button className="primary-button" disabled={loading}>{loading ? 'Signing in…' : 'Sign in securely'}</button>
        </form>
      </section>
    </main>
  );
}

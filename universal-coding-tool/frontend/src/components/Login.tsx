import { FormEvent, useState } from 'react';
import { login } from '../api/client';

interface Props {
  onSuccess: () => void;
}

export default function Login({ onSuccess }: Props) {
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('changeme');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      onSuccess();
    } catch (err) {
      setError('Unable to log in. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form className="card" onSubmit={handleSubmit}>
        <h1>Universal Coding Tool</h1>
        <p>Sign in with the credentials configured on the backend.</p>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
        </label>
        <label>
          Password
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  );
}

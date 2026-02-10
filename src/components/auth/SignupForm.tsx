import { useState } from 'react';
import { UserPlus, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { signupSchema } from '../../types';
import { Spinner } from '../ui/Spinner';

export function SignupForm() {
  const { signUp } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = signupSchema.safeParse({ email, password, fullName });
    if (!result.success) {
      setError(result.error.issues[0].message);
      return;
    }

    setLoading(true);
    const { error: authError } = await signUp(email, password, fullName);
    if (authError) setError(authError);
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm px-4 py-3 rounded-lg animate-fade-in">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-surface-300 mb-1.5">Full name</label>
        <input
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="input-field"
          placeholder="John Doe"
          autoComplete="name"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-surface-300 mb-1.5">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input-field"
          placeholder="you@example.com"
          autoComplete="email"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-surface-300 mb-1.5">Password</label>
        <div className="relative">
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-field pr-10"
            placeholder="Min. 6 characters"
            autoComplete="new-password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white transition-colors"
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
        {loading ? <Spinner size="sm" /> : <UserPlus size={18} />}
        {loading ? 'Creating account...' : 'Create account'}
      </button>
    </form>
  );
}

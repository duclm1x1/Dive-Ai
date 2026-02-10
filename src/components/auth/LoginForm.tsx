import { useState } from 'react';
import { LogIn, Eye, EyeOff, Terminal, Zap, Shield } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { loginSchema } from '../../types';
import { Spinner } from '../ui/Spinner';

export function LoginForm() {
  const { signIn, signInAsGuest } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = loginSchema.safeParse({ email, password });
    if (!result.success) {
      setError(result.error.issues[0].message);
      return;
    }

    setLoading(true);
    const { error: authError } = await signIn(email, password);
    if (authError) setError(authError);
    setLoading(false);
  };

  const handleGuestLogin = async () => {
    setLoading(true);
    setError('');
    await signInAsGuest();
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-3 sm:col-span-1">
          <button
            type="button"
            onClick={handleGuestLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-surface-700 bg-surface-900 hover:bg-surface-800 text-surface-300 hover:text-white transition-all disabled:opacity-50 text-sm"
          >
            <Terminal size={16} />
            <span>Try Demo</span>
          </button>
        </div>
        <div className="col-span-3 sm:col-span-2 relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-surface-800" />
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="bg-surface-950 px-3 text-surface-500 uppercase tracking-wider">Or continue with email</span>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm px-4 py-3 rounded-lg animate-fade-in flex items-start gap-2">
            <Shield size={16} className="flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5">
            Email address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-field"
            placeholder="you@company.com"
            autoComplete="email"
            disabled={loading}
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-sm font-medium text-surface-300">
              Password
            </label>
            <button
              type="button"
              className="text-xs text-brand-400 hover:text-brand-300 transition-colors"
            >
              Forgot password?
            </button>
          </div>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field pr-10"
              placeholder="Enter your password"
              autoComplete="current-password"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white transition-colors"
              tabIndex={-1}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer group">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="w-4 h-4 rounded border-surface-700 bg-surface-800 text-brand-600 focus:ring-2 focus:ring-brand-600 focus:ring-offset-0 transition-colors"
              disabled={loading}
            />
            <span className="text-sm text-surface-400 group-hover:text-surface-300 transition-colors select-none">
              Remember me for 30 days
            </span>
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2 group"
        >
          {loading ? (
            <>
              <Spinner size="sm" />
              <span>Signing in...</span>
            </>
          ) : (
            <>
              <LogIn size={18} className="group-hover:translate-x-0.5 transition-transform" />
              <span>Sign in to your account</span>
            </>
          )}
        </button>
      </form>

      <div className="pt-4 border-t border-surface-800/50">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-surface-900/50 rounded-lg px-2 py-2.5 border border-surface-800/50">
            <Zap size={14} className="text-brand-400 mx-auto mb-1" />
            <p className="text-[10px] text-surface-500 uppercase tracking-wider">Fast</p>
          </div>
          <div className="bg-surface-900/50 rounded-lg px-2 py-2.5 border border-surface-800/50">
            <Shield size={14} className="text-emerald-400 mx-auto mb-1" />
            <p className="text-[10px] text-surface-500 uppercase tracking-wider">Secure</p>
          </div>
          <div className="bg-surface-900/50 rounded-lg px-2 py-2.5 border border-surface-800/50">
            <Terminal size={14} className="text-cyan-400 mx-auto mb-1" />
            <p className="text-[10px] text-surface-500 uppercase tracking-wider">Powerful</p>
          </div>
        </div>
      </div>
    </div>
  );
}

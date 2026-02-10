import { useState } from 'react';
import { Brain } from 'lucide-react';
import { LoginForm } from './LoginForm';
import { SignupForm } from './SignupForm';

export function AuthPage() {
  const [mode, setMode] = useState<'login' | 'signup'>('login');

  return (
    <div className="min-h-screen bg-surface-950 flex">
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-950 via-surface-900 to-surface-950" />
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500 rounded-full blur-[128px]" />
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-cyan-500 rounded-full blur-[96px]" />
        </div>
        <div className="relative z-10 flex flex-col justify-center px-16">
          <div className="flex items-center gap-3 mb-8">
            <div className="h-12 w-12 rounded-xl bg-brand-600 flex items-center justify-center">
              <Brain size={28} className="text-white" />
            </div>
            <span className="text-3xl font-bold text-white">Dive AI</span>
          </div>
          <h1 className="text-4xl font-bold text-white leading-tight mb-4">
            Your intelligent<br />workspace for AI
          </h1>
          <p className="text-lg text-surface-300 max-w-md leading-relaxed">
            Collaborate with AI agents, manage conversations across workspaces, and build intelligent workflows -- all in one unified platform.
          </p>
          <div className="mt-12 flex gap-6">
            {[
              { label: 'Workspaces', value: 'Team-first' },
              { label: 'AI Models', value: 'Multi-provider' },
              { label: 'Agents', value: 'Autonomous' },
            ].map((stat) => (
              <div key={stat.label}>
                <div className="text-sm text-brand-400 font-medium">{stat.value}</div>
                <div className="text-sm text-surface-400 mt-0.5">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <div className="h-10 w-10 rounded-xl bg-brand-600 flex items-center justify-center">
              <Brain size={22} className="text-white" />
            </div>
            <span className="text-2xl font-bold text-white">Dive AI</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white">
              {mode === 'login' ? 'Welcome back' : 'Create your account'}
            </h2>
            <p className="text-surface-400 mt-1">
              {mode === 'login'
                ? 'Sign in to continue to Dive AI'
                : 'Get started with Dive AI'}
            </p>
          </div>

          {mode === 'login' ? <LoginForm /> : <SignupForm />}

          <p className="text-center text-sm text-surface-400 mt-6">
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button
              onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}
              className="text-brand-400 hover:text-brand-300 font-medium transition-colors"
            >
              {mode === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

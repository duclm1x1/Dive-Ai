import { useState } from 'react';
import { Layers, ArrowRight } from 'lucide-react';
import { CreateWorkspaceModal } from './CreateWorkspaceModal';

export function OnboardingView() {
  const [showCreate, setShowCreate] = useState(false);

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="text-center max-w-md animate-slide-up">
        <div className="h-20 w-20 rounded-2xl bg-brand-600/20 border border-brand-600/30 flex items-center justify-center mx-auto mb-6">
          <Layers size={36} className="text-brand-400" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-3">Welcome to Dive AI</h1>
        <p className="text-surface-400 text-lg leading-relaxed mb-8">
          Create your first workspace to start collaborating with AI agents and managing conversations.
        </p>
        <button
          onClick={() => setShowCreate(true)}
          className="btn-primary inline-flex items-center gap-2 text-base px-6 py-3"
        >
          Create your workspace
          <ArrowRight size={18} />
        </button>
      </div>

      <CreateWorkspaceModal open={showCreate} onClose={() => setShowCreate(false)} />
    </div>
  );
}

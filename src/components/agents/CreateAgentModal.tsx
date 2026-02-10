import { useState } from 'react';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { useCreateAgent } from '../../hooks/useAgents';
import { createAgentSchema } from '../../types';
import { Modal } from '../ui/Modal';
import { Spinner } from '../ui/Spinner';

interface Props {
  open: boolean;
  onClose: () => void;
}

const models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'llama-3', 'mistral-7b'];

export function CreateAgentModal({ open, onClose }: Props) {
  const { currentWorkspace } = useWorkspace();
  const createAgent = useCreateAgent();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [model, setModel] = useState('gpt-4');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = createAgentSchema.safeParse({ name, description, systemPrompt, model });
    if (!result.success) {
      setError(result.error.issues[0].message);
      return;
    }

    if (!currentWorkspace) return;

    try {
      await createAgent.mutateAsync({
        workspaceId: currentWorkspace.id,
        name,
        description,
        systemPrompt,
        model,
      });
      setName('');
      setDescription('');
      setSystemPrompt('');
      setModel('gpt-4');
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create agent');
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Create Agent" maxWidth="max-w-lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5">Agent name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input-field"
            placeholder="Research Assistant"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5">Description</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input-field"
            placeholder="What does this agent do?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5">Model</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="input-field"
          >
            {models.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5">System Prompt</label>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            className="input-field resize-none h-28"
            placeholder="You are a helpful assistant that..."
          />
        </div>

        <div className="flex gap-3 justify-end pt-2">
          <button type="button" onClick={onClose} className="btn-ghost">Cancel</button>
          <button type="submit" disabled={createAgent.isPending} className="btn-primary flex items-center gap-2">
            {createAgent.isPending && <Spinner size="sm" />}
            Create Agent
          </button>
        </div>
      </form>
    </Modal>
  );
}

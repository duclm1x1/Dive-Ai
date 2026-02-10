import { useState } from 'react';
import { supabase } from '../../lib/supabase';
import { useAuth } from '../../contexts/AuthContext';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { createWorkspaceSchema } from '../../types';
import { slugify } from '../../lib/utils';
import { Modal } from '../ui/Modal';
import { Spinner } from '../ui/Spinner';

interface Props {
  open: boolean;
  onClose: () => void;
}

export function CreateWorkspaceModal({ open, onClose }: Props) {
  const { user } = useAuth();
  const { refetch, setCurrentWorkspace } = useWorkspace();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = createWorkspaceSchema.safeParse({ name, description });
    if (!result.success) {
      setError(result.error.issues[0].message);
      return;
    }

    setLoading(true);
    const slug = slugify(name) + '-' + Date.now().toString(36);

    const { data, error: dbError } = await supabase
      .from('workspaces')
      .insert({ name, slug, description, owner_id: user!.id })
      .select()
      .single();

    if (dbError) {
      setError(dbError.message);
      setLoading(false);
      return;
    }

    await refetch();
    setCurrentWorkspace(data);
    setName('');
    setDescription('');
    setLoading(false);
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} title="Create Workspace">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5">Workspace name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input-field"
            placeholder="My Team"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input-field resize-none h-20"
            placeholder="What is this workspace for?"
          />
        </div>

        <div className="flex gap-3 justify-end pt-2">
          <button type="button" onClick={onClose} className="btn-ghost">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
            {loading && <Spinner size="sm" />}
            Create
          </button>
        </div>
      </form>
    </Modal>
  );
}

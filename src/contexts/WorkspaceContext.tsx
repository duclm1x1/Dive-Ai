import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from './AuthContext';
import type { Workspace } from '../types';

const GUEST_WORKSPACE: Workspace = {
  id: '00000000-0000-0000-0000-000000000001',
  owner_id: '00000000-0000-0000-0000-000000000000',
  name: 'My Workspace',
  slug: 'my-workspace',
  description: 'Default workspace',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

interface WorkspaceContextType {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  setCurrentWorkspace: (ws: Workspace | null) => void;
  loading: boolean;
  refetch: () => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { user, isGuest } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchWorkspaces = async () => {
    if (isGuest) {
      setWorkspaces([GUEST_WORKSPACE]);
      setCurrentWorkspace(GUEST_WORKSPACE);
      setLoading(false);
      return;
    }

    if (!user) {
      setWorkspaces([]);
      setCurrentWorkspace(null);
      setLoading(false);
      return;
    }

    const { data } = await supabase
      .from('workspaces')
      .select('*')
      .order('created_at', { ascending: false });

    const list = (data ?? []) as Workspace[];
    setWorkspaces(list);

    if (!currentWorkspace && list.length > 0) {
      const savedId = localStorage.getItem('dive_current_workspace');
      const saved = list.find((w) => w.id === savedId);
      setCurrentWorkspace(saved ?? list[0]);
    } else if (currentWorkspace && !list.find((w) => w.id === currentWorkspace.id)) {
      setCurrentWorkspace(list[0] ?? null);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchWorkspaces();
  }, [user, isGuest]);

  useEffect(() => {
    if (currentWorkspace) {
      localStorage.setItem('dive_current_workspace', currentWorkspace.id);
    }
  }, [currentWorkspace]);

  return (
    <WorkspaceContext.Provider
      value={{ workspaces, currentWorkspace, setCurrentWorkspace, loading, refetch: fetchWorkspaces }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error('useWorkspace must be used within WorkspaceProvider');
  return ctx;
}

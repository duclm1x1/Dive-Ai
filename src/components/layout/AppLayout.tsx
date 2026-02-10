import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { KeyboardShortcuts } from '../ui/KeyboardShortcuts';

export function AppLayout() {
  const [connected] = useState(true);

  const model = (() => {
    try {
      const c = localStorage.getItem('dive_llm_config');
      return c ? JSON.parse(c).model : 'gpt-4o-mini';
    } catch { return 'gpt-4o-mini'; }
  })();

  return (
    <div className="flex h-screen overflow-hidden bg-surface-950">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header connected={connected} model={model} />
        <main className="flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
      <KeyboardShortcuts />
    </div>
  );
}

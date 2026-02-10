import type { ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 animate-fade-in">
      <div className="h-16 w-16 rounded-2xl bg-surface-800 border border-surface-700 flex items-center justify-center mb-4">
        <Icon size={28} className="text-surface-400" />
      </div>
      <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
      <p className="text-surface-400 text-sm text-center max-w-sm mb-6">{description}</p>
      {action}
    </div>
  );
}

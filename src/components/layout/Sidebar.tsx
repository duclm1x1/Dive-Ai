import { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  Brain,
  LayoutDashboard,
  MessageSquare,
  Bot,
  Settings,
  Plus,
  LogOut,
  ChevronsUpDown,
  Search,
  X,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { useConversations, useCreateConversation } from '../../hooks/useConversations';
import { Avatar } from '../ui/Avatar';
import { cn, truncate, formatRelativeTime } from '../../lib/utils';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/chat', icon: MessageSquare, label: 'Chat' },
  { to: '/agents', icon: Bot, label: 'Agents' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const { profile, isGuest, signOut } = useAuth();
  const { workspaces, currentWorkspace, setCurrentWorkspace } = useWorkspace();
  const { data: conversations } = useConversations(isGuest ? undefined : currentWorkspace?.id);
  const createConversation = useCreateConversation();
  const navigate = useNavigate();
  const location = useLocation();
  const [wsOpen, setWsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleNewChat = async () => {
    if (isGuest) {
      navigate('/chat');
      return;
    }
    if (!currentWorkspace) return;
    const conv = await createConversation.mutateAsync({ workspaceId: currentWorkspace.id });
    navigate(`/chat/${conv.id}`);
  };

  const allConversations = isGuest ? [] : (conversations ?? []);
  const filteredConversations = searchQuery
    ? allConversations.filter((c) =>
        c.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : allConversations;
  const displayConversations = filteredConversations.slice(0, 12);
  const isChatRoute = location.pathname.startsWith('/chat');

  return (
    <aside className="w-64 h-screen flex flex-col bg-surface-900 border-r border-surface-800 flex-shrink-0">
      <div className="p-4 border-b border-surface-800">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="h-8 w-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
            <Brain size={18} className="text-white" />
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-base font-bold text-white tracking-tight">Dive AI</span>
            <span className="text-[10px] text-surface-600 font-mono">v1.0</span>
          </div>
        </div>

        {!isGuest && (
          <div className="relative">
            <button
              onClick={() => setWsOpen(!wsOpen)}
              className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-surface-800/80 border border-surface-700/50 hover:border-surface-600 transition-colors"
            >
              <span className="text-xs text-surface-200 truncate font-medium">
                {currentWorkspace?.name ?? 'Select workspace'}
              </span>
              <ChevronsUpDown size={12} className="text-surface-500 flex-shrink-0" />
            </button>

            {wsOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-surface-800 border border-surface-700 rounded-lg shadow-xl z-50 py-1 animate-scale-in">
                {workspaces.map((ws) => (
                  <button
                    key={ws.id}
                    onClick={() => { setCurrentWorkspace(ws); setWsOpen(false); }}
                    className={cn(
                      'w-full text-left px-3 py-1.5 text-xs hover:bg-surface-700 transition-colors',
                      ws.id === currentWorkspace?.id ? 'text-brand-400' : 'text-surface-300'
                    )}
                  >
                    {ws.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <nav className="p-2 space-y-0.5">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150',
                isActive
                  ? 'text-white bg-surface-800 border border-surface-700/50'
                  : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50 border border-transparent'
              )
            }
          >
            <Icon size={16} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="px-3 mt-1">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 text-xs font-medium py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-all duration-200 active:scale-[0.98]"
        >
          <Plus size={14} />
          New Chat
        </button>
      </div>

      {isChatRoute && !isGuest && (
        <div className="flex-1 overflow-hidden flex flex-col mt-3 border-t border-surface-800">
          <div className="px-3 pt-3 pb-2">
            <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-surface-800/60 border border-surface-700/30">
              <Search size={12} className="text-surface-500 flex-shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search chats..."
                className="flex-1 bg-transparent text-xs text-surface-200 placeholder-surface-600 focus:outline-none"
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="text-surface-500 hover:text-surface-300">
                  <X size={10} />
                </button>
              )}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-2 pb-2">
            <p className="text-[10px] font-medium text-surface-600 uppercase tracking-wider px-2.5 mb-1.5">
              Conversations
            </p>
            <div className="space-y-px">
              {displayConversations.length === 0 && (
                <p className="text-[11px] text-surface-600 px-2.5 py-3 text-center">
                  {searchQuery ? 'No matches found' : 'No conversations yet'}
                </p>
              )}
              {displayConversations.map((c) => (
                <NavLink
                  key={c.id}
                  to={`/chat/${c.id}`}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-2 px-2.5 py-1.5 rounded-md text-[11px] transition-all duration-150',
                      isActive
                        ? 'text-white bg-surface-800'
                        : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'
                    )
                  }
                >
                  <MessageSquare size={12} className="flex-shrink-0 opacity-50" />
                  <span className="truncate flex-1">{truncate(c.title, 22)}</span>
                  <span className="text-[9px] text-surface-600 flex-shrink-0">
                    {formatRelativeTime(c.updated_at)}
                  </span>
                </NavLink>
              ))}
            </div>
          </div>
        </div>
      )}

      {(!isChatRoute || isGuest) && <div className="flex-1" />}

      <div className="p-3 border-t border-surface-800">
        <div className="flex items-center gap-2.5">
          <Avatar name={profile?.full_name || profile?.email || '?'} size="sm" />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-surface-200 truncate">{profile?.full_name || 'User'}</p>
            <p className="text-[10px] text-surface-500 truncate">{isGuest ? 'Guest mode' : profile?.email}</p>
          </div>
          {!isGuest && (
            <button
              onClick={signOut}
              className="p-1.5 rounded-md hover:bg-surface-800 text-surface-500 hover:text-white transition-colors"
              title="Sign out"
            >
              <LogOut size={14} />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}

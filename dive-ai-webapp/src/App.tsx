import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Home, MessageSquare, Code, Database, Settings, Activity } from 'lucide-react'
import HomePage from './pages/HomePage'
import ChatPage from './pages/ChatPage'
import AlgorithmsPage from './pages/AlgorithmsPage'
import EditorPage from './pages/EditorPage'
import StatsPage from './pages/StatsPage'
import './index.css'

function NavBar() {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/chat', icon: MessageSquare, label: 'AI Chat' },
    { path: '/algorithms', icon: Database, label: 'Algorithms' },
    { path: '/editor', icon: Code, label: 'Code Editor' },
    { path: '/stats', icon: Activity, label: 'Statistics' },
  ]

  return (
    <nav className="fixed left-0 top-0 h-screen w-20 glass-card m-4 flex flex-col items-center py-6 z-50">
      <div className="text-4xl mb-8 animate-glow">🦞</div>

      {navItems.map(({ path, icon: Icon, label }) => (
        <Link
          key={path}
          to={path}
          className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-all duration-300 group relative
            ${location.pathname === path
              ? 'bg-gradient-to-r from-dive-primary to-dive-secondary text-white shadow-lg shadow-dive-primary/30'
              : 'text-gray-400 hover:text-white hover:bg-dive-surface-light'
            }`}
          title={label}
        >
          <Icon size={24} />
          <span className="absolute left-full ml-4 px-3 py-1.5 bg-dive-surface rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
            {label}
          </span>
        </Link>
      ))}
    </nav>
  )
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <NavBar />
        <main className="ml-28 p-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/algorithms" element={<AlgorithmsPage />} />
            <Route path="/editor" element={<EditorPage />} />
            <Route path="/stats" element={<StatsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App

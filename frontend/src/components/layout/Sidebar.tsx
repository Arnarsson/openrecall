import { NavLink } from 'react-router-dom'
import { Clock, Search, GitBranch, Box, BarChart3, Settings, Brain } from 'lucide-react'
import { clsx } from 'clsx'

interface NavItemProps {
  to: string
  icon: React.ReactNode
  label: string
}

function NavItem({ to, icon, label }: NavItemProps) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        clsx(
          'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors',
          isActive
            ? 'bg-sidebar-active text-white'
            : 'text-gray-400 hover:bg-sidebar-hover hover:text-gray-200'
        )
      }
    >
      {icon}
      <span>{label}</span>
    </NavLink>
  )
}

interface NavSectionProps {
  title: string
  children: React.ReactNode
}

function NavSection({ title, children }: NavSectionProps) {
  return (
    <div className="mb-6">
      <h3 className="px-4 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
        {title}
      </h3>
      <nav className="space-y-1">{children}</nav>
    </div>
  )
}

export default function Sidebar() {
  return (
    <aside className="w-56 bg-sidebar h-screen flex flex-col border-r border-sidebar-border dark-scrollbar overflow-y-auto">
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-sidebar-border">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-white font-semibold text-base">TotalRecall</h1>
          <p className="text-gray-500 text-xs">MEMORY</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 py-4 px-2">
        <NavSection title="Recall">
          <NavItem to="/timeline" icon={<Clock className="w-4 h-4" />} label="Timeline" />
          <NavItem to="/search" icon={<Search className="w-4 h-4" />} label="Search" />
        </NavSection>

        <NavSection title="Knowledge">
          <NavItem to="/graph" icon={<GitBranch className="w-4 h-4" />} label="Graph" />
          <NavItem to="/entities" icon={<Box className="w-4 h-4" />} label="Entities" />
        </NavSection>

        <NavSection title="System">
          <NavItem to="/stats" icon={<BarChart3 className="w-4 h-4" />} label="Stats" />
        </NavSection>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <button className="flex items-center gap-2 text-gray-500 hover:text-gray-300 text-sm w-full px-2 py-2 rounded-lg hover:bg-sidebar-hover transition-colors">
          <Settings className="w-4 h-4" />
          <span>Configure MCP</span>
        </button>
      </div>
    </aside>
  )
}

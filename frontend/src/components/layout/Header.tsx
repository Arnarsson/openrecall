import { Clock, RefreshCw } from 'lucide-react'
import { useStatus } from '@/hooks/useStats'
import StatusIndicator from '../common/StatusIndicator'
import Badge from '../common/Badge'

interface HeaderProps {
  title: string
  icon?: React.ReactNode
}

export default function Header({ title, icon }: HeaderProps) {
  const { status, refetch } = useStatus()

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        {icon || <Clock className="w-5 h-5 text-gray-600" />}
        <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
        <Badge text={`MCP v${status?.version || '1.0.0'}`} variant="default" />
      </div>

      <div className="flex items-center gap-4">
        <StatusIndicator
          status={status?.recording ? 'active' : status?.paused ? 'paused' : 'inactive'}
          label="Memory"
        />
        <button
          onClick={() => refetch()}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>
    </header>
  )
}

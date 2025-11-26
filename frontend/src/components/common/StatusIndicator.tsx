import { clsx } from 'clsx'

interface StatusIndicatorProps {
  status: 'active' | 'paused' | 'inactive'
  label?: string
}

const statusStyles = {
  active: 'bg-green-500',
  paused: 'bg-yellow-500',
  inactive: 'bg-gray-400',
}

const statusLabels = {
  active: 'Active',
  paused: 'Paused',
  inactive: 'Inactive',
}

export default function StatusIndicator({ status, label }: StatusIndicatorProps) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-full">
      <span className={clsx('w-2 h-2 rounded-full', statusStyles[status])} />
      <span className="text-sm font-medium text-gray-700">
        {label} {statusLabels[status]}
      </span>
    </div>
  )
}

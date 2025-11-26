import { BarChart3, HardDrive, Calendar, AppWindow, Clock } from 'lucide-react'
import Header from '@/components/layout/Header'
import { useStats } from '@/hooks/useStats'
import { formatStorageSize, formatDate } from '@/utils/formatters'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  subtitle?: string
}

function StatCard({ title, value, icon, subtitle }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center gap-4">
        <div className="p-3 bg-gray-100 rounded-lg">{icon}</div>
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>}
        </div>
      </div>
    </div>
  )
}

interface AppBarProps {
  name: string
  count: number
  maxCount: number
  color: string
}

function AppBar({ name, count, maxCount, color }: AppBarProps) {
  const percentage = (count / maxCount) * 100
  return (
    <div className="flex items-center gap-3">
      <div className="w-24 text-sm text-gray-600 truncate">{name}</div>
      <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
      <div className="w-12 text-sm text-gray-500 text-right">{count}</div>
    </div>
  )
}

function HourlyActivityChart({ data }: { data: { hour: number; count: number }[] }) {
  const maxCount = Math.max(...data.map((d) => d.count), 1)

  return (
    <div className="flex items-end gap-1 h-32">
      {Array.from({ length: 24 }, (_, hour) => {
        const hourData = data.find((d) => d.hour === hour)
        const count = hourData?.count || 0
        const height = (count / maxCount) * 100
        const isWorkHour = hour >= 9 && hour <= 17

        return (
          <div key={hour} className="flex-1 flex flex-col items-center gap-1">
            <div
              className={`w-full rounded-t transition-all duration-300 ${
                isWorkHour ? 'bg-indigo-500' : 'bg-gray-300'
              }`}
              style={{ height: `${Math.max(height, 2)}%` }}
              title={`${hour}:00 - ${count} captures`}
            />
            {hour % 6 === 0 && (
              <span className="text-xs text-gray-400">{hour}</span>
            )}
          </div>
        )
      })}
    </div>
  )
}

const APP_COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316',
  '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6'
]

export default function StatsPage() {
  const { stats, loading, error } = useStats()

  if (loading) {
    return (
      <>
        <Header title="Stats" icon={<BarChart3 className="w-5 h-5 text-gray-600" />} />
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
        </div>
      </>
    )
  }

  if (error || !stats) {
    return (
      <>
        <Header title="Stats" icon={<BarChart3 className="w-5 h-5 text-gray-600" />} />
        <div className="flex-1 flex items-center justify-center text-red-500">
          Failed to load statistics
        </div>
      </>
    )
  }

  return (
    <>
      <Header title="Stats" icon={<BarChart3 className="w-5 h-5 text-gray-600" />} />

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Captures"
            value={stats.total_entries.toLocaleString()}
            icon={<Calendar className="w-5 h-5 text-indigo-500" />}
          />
          <StatCard
            title="Storage Used"
            value={formatStorageSize(stats.storage_used_mb)}
            icon={<HardDrive className="w-5 h-5 text-purple-500" />}
          />
          <StatCard
            title="Apps Tracked"
            value={stats.apps.length}
            icon={<AppWindow className="w-5 h-5 text-pink-500" />}
          />
          <StatCard
            title="Recording Since"
            value={stats.date_range.first_entry ? formatDate(stats.date_range.first_entry) : 'N/A'}
            icon={<Clock className="w-5 h-5 text-blue-500" />}
          />
        </div>

        {/* Activity by Hour */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Activity by Hour</h3>
          <HourlyActivityChart data={stats.activity_by_hour} />
          <div className="flex justify-between mt-2 text-xs text-gray-400">
            <span>12 AM</span>
            <span>6 AM</span>
            <span>12 PM</span>
            <span>6 PM</span>
            <span>12 AM</span>
          </div>
        </div>

        {/* Top Apps */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Applications</h3>
          <div className="space-y-3">
            {stats.apps.slice(0, 10).map((app, index) => (
              <AppBar
                key={app.name}
                name={app.name}
                count={app.count}
                maxCount={stats.apps[0]?.count || 1}
                color={APP_COLORS[index % APP_COLORS.length]}
              />
            ))}
          </div>
          {stats.apps.length === 0 && (
            <p className="text-gray-500 text-center py-4">No app data available yet</p>
          )}
        </div>
      </div>
    </>
  )
}

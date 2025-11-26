import { Code, Globe, MessageSquare, Palette, FileText, Monitor, Music, Folder } from 'lucide-react'
import type { Entry } from '@/types'
import { formatTime, truncateText } from '@/utils/formatters'
import Tag from '../common/Tag'

interface ObservationCardProps {
  entry: Entry
  onClick?: () => void
}

// Map app categories to icons
function getAppIcon(app: string, tags: string[]) {
  const appLower = app.toLowerCase()
  const category = tags[0]?.toLowerCase()

  if (category === 'development' || appLower.includes('code') || appLower.includes('terminal')) {
    return <Code className="w-4 h-4 text-blue-500" />
  }
  if (category === 'browser' || appLower.includes('chrome') || appLower.includes('firefox') || appLower.includes('safari')) {
    return <Globe className="w-4 h-4 text-green-500" />
  }
  if (category === 'communication' || appLower.includes('slack') || appLower.includes('discord') || appLower.includes('teams')) {
    return <MessageSquare className="w-4 h-4 text-purple-500" />
  }
  if (category === 'design' || appLower.includes('figma') || appLower.includes('sketch')) {
    return <Palette className="w-4 h-4 text-pink-500" />
  }
  if (category === 'productivity' || appLower.includes('notion') || appLower.includes('word')) {
    return <FileText className="w-4 h-4 text-orange-500" />
  }
  if (category === 'media' || appLower.includes('spotify') || appLower.includes('music')) {
    return <Music className="w-4 h-4 text-green-500" />
  }
  if (category === 'system' || appLower.includes('finder') || appLower.includes('explorer')) {
    return <Folder className="w-4 h-4 text-yellow-500" />
  }
  return <Monitor className="w-4 h-4 text-gray-500" />
}

export default function ObservationCard({ entry, onClick }: ObservationCardProps) {
  const textPreview = entry.text ? truncateText(entry.text, 120) : ''

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md hover:border-gray-300 transition-all cursor-pointer group"
    >
      {/* Screenshot thumbnail */}
      <div className="relative aspect-video bg-gray-100 overflow-hidden">
        <img
          src={entry.screenshot_url}
          alt={`Screenshot from ${entry.app}`}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
        {/* Timestamp badge */}
        <div className="absolute top-2 right-2 px-2 py-1 bg-black/70 rounded text-white text-xs font-medium">
          {formatTime(entry.timestamp)}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* App info */}
        <div className="flex items-center gap-2 mb-2">
          {getAppIcon(entry.app, entry.tags)}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5">
              <span className="font-medium text-gray-900 text-sm">{entry.app}</span>
              {entry.title && (
                <>
                  <span className="text-gray-400">—</span>
                  <span className="text-gray-500 text-sm truncate">{entry.title}</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Text preview */}
        {textPreview && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">{textPreview}</p>
        )}

        {/* Tags */}
        {entry.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {entry.tags.slice(0, 3).map((tag) => (
              <Tag key={tag} label={tag} />
            ))}
            {entry.tags.length > 3 && (
              <span className="text-xs text-gray-400">+{entry.tags.length - 3}</span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

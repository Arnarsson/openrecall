import { useEffect } from 'react'
import { X } from 'lucide-react'
import type { Entry } from '@/types'
import { formatDateTime } from '@/utils/formatters'
import Tag from './Tag'

interface ScreenshotModalProps {
  entry: Entry | null
  isOpen: boolean
  onClose: () => void
}

export default function ScreenshotModal({ entry, isOpen, onClose }: ScreenshotModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen || !entry) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
      onClick={onClose}
    >
      <div
        className="relative max-w-[95vw] max-h-[95vh] bg-white rounded-lg shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900">{entry.app}</span>
              {entry.title && (
                <>
                  <span className="text-gray-400">—</span>
                  <span className="text-gray-600 truncate max-w-md">{entry.title}</span>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">{formatDateTime(entry.timestamp)}</span>
            <button
              onClick={onClose}
              className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Image */}
        <div className="overflow-auto max-h-[calc(95vh-120px)]">
          <img
            src={entry.screenshot_url}
            alt={`Screenshot from ${entry.app}`}
            className="w-full h-auto"
          />
        </div>

        {/* Footer with tags and text */}
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center gap-2 mb-2">
            {entry.tags.map((tag) => (
              <Tag key={tag} label={tag} />
            ))}
          </div>
          {entry.text && (
            <p className="text-sm text-gray-600 line-clamp-2">{entry.text}</p>
          )}
        </div>
      </div>
    </div>
  )
}

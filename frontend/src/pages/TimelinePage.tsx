import { useState, useEffect, useCallback } from 'react'
import { Clock } from 'lucide-react'
import Header from '@/components/layout/Header'
import CardGrid from '@/components/cards/CardGrid'
import { getEntries } from '@/api/client'
import type { Entry, PaginatedResponse } from '@/types'

export default function TimelinePage() {
  const [entries, setEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)

  const fetchEntries = useCallback(async (pageNum: number, append: boolean = false) => {
    if (pageNum === 1) {
      setLoading(true)
    } else {
      setLoadingMore(true)
    }

    try {
      const data = await getEntries({ page: pageNum, limit: 20 }) as PaginatedResponse
      if (append) {
        setEntries((prev) => [...prev, ...data.entries])
      } else {
        setEntries(data.entries)
      }
      setHasMore(data.has_more)
    } catch (error) {
      console.error('Failed to fetch entries:', error)
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }, [])

  useEffect(() => {
    fetchEntries(1)
  }, [fetchEntries])

  const loadMore = () => {
    if (!loadingMore && hasMore) {
      const nextPage = page + 1
      setPage(nextPage)
      fetchEntries(nextPage, true)
    }
  }

  // Infinite scroll handler
  useEffect(() => {
    const handleScroll = () => {
      const scrollContainer = document.querySelector('.overflow-y-auto')
      if (!scrollContainer) return

      const { scrollTop, scrollHeight, clientHeight } = scrollContainer
      if (scrollHeight - scrollTop - clientHeight < 200 && !loadingMore && hasMore) {
        loadMore()
      }
    }

    const scrollContainer = document.querySelector('.overflow-y-auto')
    scrollContainer?.addEventListener('scroll', handleScroll)
    return () => scrollContainer?.removeEventListener('scroll', handleScroll)
  }, [loadingMore, hasMore, page])

  return (
    <>
      <Header title="Observation Stream" icon={<Clock className="w-5 h-5 text-gray-600" />} />

      <div className="flex-1 overflow-y-auto p-6">
        <CardGrid
          entries={entries}
          loading={loading}
          emptyMessage="No observations yet. Start recording to see your activity here."
        />

        {/* Load more indicator */}
        {loadingMore && (
          <div className="flex justify-center py-8">
            <div className="flex items-center gap-2 text-gray-500">
              <div className="w-5 h-5 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
              <span>Loading more...</span>
            </div>
          </div>
        )}

        {/* Load more button (fallback) */}
        {hasMore && !loadingMore && (
          <div className="flex justify-center py-8">
            <button
              onClick={loadMore}
              className="px-6 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Load More
            </button>
          </div>
        )}
      </div>
    </>
  )
}

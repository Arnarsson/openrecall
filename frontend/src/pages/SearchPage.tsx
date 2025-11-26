import { useState, FormEvent } from 'react'
import { Search, X } from 'lucide-react'
import Header from '@/components/layout/Header'
import CardGrid from '@/components/cards/CardGrid'
import { useSearch } from '@/hooks/useSearch'

export default function SearchPage() {
  const [inputValue, setInputValue] = useState('')
  const { results, loading, error, query, search, clear } = useSearch()

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      search(inputValue.trim())
    }
  }

  const handleClear = () => {
    setInputValue('')
    clear()
  }

  return (
    <>
      <Header title="Search" icon={<Search className="w-5 h-5 text-gray-600" />} />

      <div className="flex-1 overflow-y-auto">
        {/* Search Bar */}
        <div className="sticky top-0 bg-gray-50 border-b border-gray-200 p-6 z-10">
          <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Search your memories... (e.g., 'react component', 'meeting notes')"
                className="w-full pl-12 pr-12 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              {inputValue && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          </form>

          {/* Results summary */}
          {query && !loading && (
            <div className="max-w-2xl mx-auto mt-3 text-sm text-gray-600">
              Found {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
            </div>
          )}
        </div>

        {/* Results */}
        <div className="p-6">
          {error ? (
            <div className="flex flex-col items-center justify-center py-16 text-red-500">
              <p className="text-lg">Search failed: {error.message}</p>
            </div>
          ) : !query && !loading ? (
            <div className="flex flex-col items-center justify-center py-16 text-gray-500">
              <Search className="w-12 h-12 mb-4 text-gray-300" />
              <p className="text-lg">Search your observation history</p>
              <p className="text-sm mt-1">Use natural language to find past activities</p>
            </div>
          ) : (
            <CardGrid
              entries={results}
              loading={loading}
              emptyMessage={query ? `No results found for "${query}"` : undefined}
            />
          )}
        </div>
      </div>
    </>
  )
}

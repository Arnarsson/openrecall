import { useState, useCallback } from 'react';
import { searchEntries } from '@/api/client';
import type { SearchResult, SearchResponse } from '@/types';

export function useSearch() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [query, setQuery] = useState('');

  const search = useCallback(async (searchQuery: string, limit: number = 20) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setQuery('');
      return;
    }

    setLoading(true);
    setError(null);
    setQuery(searchQuery);

    try {
      const data = await searchEntries(searchQuery, limit) as SearchResponse;
      setResults(data.results);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Search failed'));
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setResults([]);
    setQuery('');
    setError(null);
  }, []);

  return { results, loading, error, query, search, clear };
}

import { useState, useEffect, useCallback } from 'react';
import { getEntries } from '@/api/client';
import type { Entry, PaginatedResponse } from '@/types';

interface UseEntriesOptions {
  page?: number;
  limit?: number;
  app?: string;
}

export function useEntries(options: UseEntriesOptions = {}) {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  const fetchEntries = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEntries(options) as PaginatedResponse;
      setEntries(data.entries);
      setTotal(data.total);
      setHasMore(data.has_more);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch entries'));
    } finally {
      setLoading(false);
    }
  }, [options.page, options.limit, options.app]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  return { entries, loading, error, total, hasMore, refetch: fetchEntries };
}

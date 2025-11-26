export interface Entry {
  id: number;
  app: string;
  title: string;
  text: string;
  timestamp: number;
  screenshot_url: string;
  formatted_time: string;
  relative_time: string;
  tags: string[];
}

export interface SearchResult extends Entry {
  similarity_score: number;
}

export interface AppStats {
  name: string;
  count: number;
  category: string | null;
}

export interface HourlyActivity {
  hour: number;
  count: number;
}

export interface SystemStats {
  total_entries: number;
  storage_used_mb: number;
  date_range: {
    first_entry: number | null;
    last_entry: number | null;
  };
  apps: AppStats[];
  activity_by_hour: HourlyActivity[];
  memory_status: 'active' | 'paused' | 'inactive';
  version: string;
}

export interface PaginatedResponse {
  entries: Entry[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}

export interface TimelineData {
  timestamps: number[];
  date_range: {
    start: number | null;
    end: number | null;
  };
  total_count: number;
}

export interface StatusResponse {
  status: 'active' | 'inactive';
  recording: boolean;
  paused: boolean;
  last_capture: number | null;
  version: string;
}

export interface AppsResponse {
  apps: AppStats[];
}

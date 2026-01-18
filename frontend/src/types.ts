// API response types
export interface UploadResponse {
  job_id: string;
}

export interface Video {
  id: string;
  video_url: string;
  caption: string;
}

export interface FeedResponse {
  videos: Video[];
  next_cursor?: string;
}

export type JobStatus = 'processing' | 'done' | 'failed';

export interface StatusResponse {
  status: JobStatus;
  progress: number; // 0-100
  message?: string;
  estimated_time_remaining?: number; // seconds
}

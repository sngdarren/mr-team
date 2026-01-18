import { API_ENDPOINTS } from '../config';
import { UploadResponse, FeedResponse, StatusResponse, JobStatus } from '../types';

type BackendFeedResponse = {
  job_id: string;
  videos: string[];
  count: number;
};

type BackendStatusResponse = {
  job_id: string;
  status: JobStatus;
};

/**
 * Upload a PDF file to the backend
 * Returns a job_id that can be used to fetch generated videos
 */
export async function uploadPDF(fileUri: string, fileName: string): Promise<UploadResponse> {
  const formData = new FormData();

  // Create file object for upload
  formData.append('pdf', {
    uri: fileUri,
    name: fileName,
    type: 'application/pdf',
  } as any);

  try {
    console.log('[API] Uploading PDF to:', API_ENDPOINTS.UPLOAD_PDF);
    console.log('[API] File URI:', fileUri);
    console.log('[API] File Name:', fileName);

    const response = await fetch(API_ENDPOINTS.UPLOAD_PDF, {
      method: 'POST',
      body: formData,
      // Let fetch automatically set Content-Type with boundary
    });

    console.log('[API] Response status:', response.status);
    console.log('[API] Response headers:', JSON.stringify([...response.headers.entries()]));

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[API] Upload failed:', errorText);
      throw new Error(`Upload failed with status ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('[API] Upload successful:', data);
    return data;
  } catch (error) {
    console.error('[API] Upload error:', error);
    throw error;
  }
}

/**
 * Check the processing status of a job
 * Returns status, progress, and estimated time remaining
 */
export async function checkJobStatus(jobId: string): Promise<StatusResponse> {
  const url = `${API_ENDPOINTS.GET_STATUS}/${jobId}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Status check failed: ${response.statusText}`);
  }

  const data = (await response.json()) as BackendStatusResponse;
  const status = data.status ?? 'processing';
  const progress = status === 'done' ? 100 : 0;

  return {
    status,
    progress,
  };
}

/**
 * Custom error class for job not found errors
 */
export class JobNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'JobNotFoundError';
  }
}

/**
 * Fetch video feed for a given job_id
 * Supports pagination via cursor
 */
export async function fetchFeed(jobId: string, cursor?: string): Promise<FeedResponse> {
  const url = `${API_ENDPOINTS.GET_FEED}/${jobId}/list`;
  const response = await fetch(url);

  if (!response.ok) {
    if (response.status === 404) {
      throw new JobNotFoundError(`Job not found: ${jobId}`);
    }
    throw new Error(`Fetch feed failed: ${response.statusText}`);
  }

  const data = (await response.json()) as BackendFeedResponse;
  const videos = (data.videos || []).map((videoIdOrPath) => ({
    id: String(videoIdOrPath),
    video_url: `${API_ENDPOINTS.GET_FEED}/${encodeURIComponent(String(videoIdOrPath))}`,
    caption: '',
  }));

  return {
    videos,
  };
}

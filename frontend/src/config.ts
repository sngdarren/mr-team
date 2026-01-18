// Backend API configuration
// Update this to your actual backend URL

// For iPhone/physical device - use your Mac's local IP:
// Real backend (Python/FastAPI) runs on port 8000
export const API_BASE_URL = 'http://172.20.10.15:8000';

// For iOS Simulator or Android Emulator (on same machine):
// export const API_BASE_URL = 'http://localhost:3000';


// API endpoints
export const API_ENDPOINTS = {
  UPLOAD_PDF: `${API_BASE_URL}/generate`,
  GET_STATUS: `${API_BASE_URL}/status`,
  GET_FEED: `${API_BASE_URL}/videos`,
  GET_VIDEO: `${API_BASE_URL}/videos`,
};

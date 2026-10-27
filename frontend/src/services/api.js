/**
 * ImageProof Frontend API Service
 * Centralized HTTP Client connecting to the Flask Backend.
 */

// Base URL for backend Flask API
// In development: points to local Flask server (http://localhost:5000/api)
// In production (Vercel): points to relative '/api' on the same live domain
export const API_BASE_URL = import.meta.env.PROD 
  ? '/api' 
  : 'http://localhost:5000/api';

/**
 * Helper to process Fetch API responses and normalize errors.
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `Server error (${response.status})`;
    try {
      const errorData = await response.json();
      if (errorData.error) {
        errorMessage = errorData.error;
      }
    } catch {
      // Non-JSON error body (e.g. 500 HTML or 413)
      if (response.status === 413) {
        errorMessage = 'File too large. Maximum allowed size is 16MB.';
      }
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

/**
 * Checks if Flask backend server is alive and reachable.
 */
export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return await handleResponse(res);
  } catch (err) {
    return {
      status: 'offline',
      error: 'Backend is currently offline or unreachable at ' + API_BASE_URL
    };
  }
}

/**
 * Fetches dashboard summary statistics.
 */
export async function fetchDashboardStats() {
  const res = await fetch(`${API_BASE_URL}/stats`);
  return await handleResponse(res);
}

/**
 * Uploads an image file with optional case parameters for forensic analysis.
 * @param {FormData} formData - Multipart form containing image, case_id, notes
 */
export async function uploadAndAnalyzeImage(formData) {
  const res = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });
  return await handleResponse(res);
}

/**
 * Fetches past analysis records with optional search filter.
 */
export async function fetchHistory(searchQuery = '') {
  const url = searchQuery 
    ? `${API_BASE_URL}/history?search=${encodeURIComponent(searchQuery)}`
    : `${API_BASE_URL}/history`;
  const res = await fetch(url);
  return await handleResponse(res);
}

/**
 * Fetches full record for a specific analysis ID.
 */
export async function fetchAnalysisById(id) {
  const res = await fetch(`${API_BASE_URL}/analysis/${id}`);
  return await handleResponse(res);
}

/**
 * Returns direct download URL for a generated PDF report by filename.
 */
export function getReportDownloadUrl(filename) {
  if (!filename) return '#';
  return `${API_BASE_URL}/reports/${encodeURIComponent(filename)}`;
}

/**
 * Returns direct download URL for an analysis record's PDF report by ID.
 */
export function getAnalysisReportUrl(id) {
  return `${API_BASE_URL}/analysis/${id}/report`;
}

/**
 * Returns direct URL for viewing an uploaded image.
 */
export function getImageUrl(filename) {
  if (!filename) return '';
  return `${API_BASE_URL}/uploads/${encodeURIComponent(filename)}`;
}

/**
 * Deletes an analysis record and its server files.
 */
export async function deleteAnalysisRecord(id) {
  const res = await fetch(`${API_BASE_URL}/analysis/${id}`, {
    method: 'DELETE',
  });
  return await handleResponse(res);
}

/**
 * Resets the SQLite database and clears all uploaded images/reports.
 */
export async function resetAllData() {
  const res = await fetch(`${API_BASE_URL}/reset`, {
    method: 'POST',
  });
  return await handleResponse(res);
}

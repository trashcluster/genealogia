import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/api/auth/login', credentials),
  register: (userData: { username: string; email: string; password: string }) =>
    api.post('/api/auth/register', userData),
  getCurrentUser: () => api.get('/api/auth/me'),
};

export const individualsAPI = {
  getAll: () => api.get('/api/individuals'),
  getById: (id: string) => api.get(`/api/individuals/${id}`),
  create: (data: any) => api.post('/api/individuals', data),
  update: (id: string, data: any) => api.put(`/api/individuals/${id}`, data),
  delete: (id: string) => api.delete(`/api/individuals/${id}`),
  search: (query: string) => api.get(`/api/individuals/search?q=${query}`),
};

export const familiesAPI = {
  getAll: () => api.get('/api/families'),
  getById: (id: string) => api.get(`/api/families/${id}`),
  create: (data: any) => api.post('/api/families', data),
  update: (id: string, data: any) => api.put(`/api/families/${id}`, data),
  delete: (id: string) => api.delete(`/api/families/${id}`),
};

export const eventsAPI = {
  getAll: () => api.get('/api/events'),
  getById: (id: string) => api.get(`/api/events/${id}`),
  create: (data: any) => api.post('/api/events', data),
  update: (id: string, data: any) => api.put(`/api/events/${id}`, data),
  delete: (id: string) => api.delete(`/api/events/${id}`),
  getTimeline: () => api.get('/api/events/timeline'),
};

export const mediaAPI = {
  getAll: () => api.get('/api/media'),
  getById: (id: string) => api.get(`/api/media/${id}`),
  upload: (formData: FormData) => api.post('/api/media/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id: string) => api.delete(`/api/media/${id}`),
};

export const ingestionAPI = {
  processText: (data: { text: string; source?: string }) =>
    api.post('/api/ingestion/text', data),
  processVoice: (formData: FormData) =>
    api.post('/api/ingestion/voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  processDocument: (formData: FormData) =>
    api.post('/api/ingestion/document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getHistory: () => api.get('/api/ingestion/history'),
  getStatus: (id: string) => api.get(`/api/ingestion/status/${id}`),
};

export const knowledgeAPI = {
  getAll: () => api.get('/api/knowledge/documents'),
  getById: (id: string) => api.get(`/api/knowledge/documents/${id}`),
  upload: (formData: FormData) =>
    api.post('/api/knowledge/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  search: (query: string) => api.get(`/api/knowledge/search?q=${query}`),
  semanticSearch: (query: string) => api.post('/api/knowledge/semantic-search', { query }),
  getEvents: () => api.get('/api/knowledge/events'),
  getTimeline: () => api.get('/api/knowledge/timeline'),
  deleteDocument: (id: string) => api.delete(`/api/knowledge/documents/${id}`),
};

export const faceRecognitionAPI = {
  detectFaces: (formData: FormData) =>
    api.post('/api/face-recognition/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  matchFaces: (data: { faceId: string; threshold?: number }) =>
    api.post('/api/face-recognition/match', data),
  registerFace: (formData: FormData) =>
    api.post('/api/face-recognition/register', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getClusters: () => api.get('/api/face-recognition/clusters'),
  getPersonFaces: (personId: string) => api.get(`/api/face-recognition/person/${personId}`),
  getStats: () => api.get('/api/face-recognition/stats'),
};

export const statsAPI = {
  getDashboard: () => api.get('/api/stats/dashboard'),
  getIngestionStats: () => api.get('/api/stats/ingestion'),
  getFaceRecognitionStats: () => api.get('/api/stats/face-recognition'),
  getKnowledgeStats: () => api.get('/api/stats/knowledge'),
};

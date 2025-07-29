import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
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

// Job API functions
export const jobApi = {
  search: (params: any) => api.get('/jobs', { params }),
  getById: (id: number) => api.get(`/jobs/${id}`),
  getRecent: (days: number = 7) => api.get('/jobs/recent', { params: { days } }),
  getByCompany: (company: string) => api.get(`/jobs/company/${company}`),
  getByLocation: (location: string) => api.get(`/jobs/location/${location}`),
  getRemote: () => api.get('/jobs/remote'),
};

// Auth API functions
export const authApi = {
  login: (credentials: { email: string; password: string }) =>
    api.post('/auth/login', credentials),
  register: (userData: any) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (userData: any) => api.put('/auth/me', userData),
  refreshToken: () => api.post('/auth/refresh'),
}; 
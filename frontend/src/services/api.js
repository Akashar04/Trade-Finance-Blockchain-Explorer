import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  signup: (userData) => api.post('/auth/signup', userData),
  getUser: (token) => {
    if (token) {
      return api.get('/auth/user', {
        headers: { Authorization: `Bearer ${token}` }
      });
    }
    return api.get('/auth/user');
  },
};

export const documentsAPI = {
  upload: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getAll: () => api.get('/documents/'),
  getById: (id) => api.get(`/documents/${id}`),
  performAction: (data) => api.post('/documents/action', data),
};

export default api;

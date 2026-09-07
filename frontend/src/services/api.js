import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Autenticação
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (email, password) => api.post('/auth/login', { email, password }),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
};

// Usuários
export const usersAPI = {
  getUser: (userId) => api.get(`/users/${userId}`),
  updateProfile: (userData) => api.put('/users/profile/update', userData),
  listAgentes: (page = 1, perPage = 10) => 
    api.get('/users/agentes', { params: { page, per_page: perPage } }),
  listClientes: (page = 1, perPage = 10) => 
    api.get('/users/clientes', { params: { page, per_page: perPage } }),
  followUser: (userId) => api.post(`/users/${userId}/follow`),
};

// Posts
export const postsAPI = {
  createPost: (postData) => api.post('/posts', postData),
  listPosts: (page = 1, perPage = 10, category = null) => 
    api.get('/posts', { params: { page, per_page: perPage, category } }),
  getPost: (postId) => api.get(`/posts/${postId}`),
  updatePost: (postId, postData) => api.put(`/posts/${postId}`, postData),
  deletePost: (postId) => api.delete(`/posts/${postId}`),
  likePost: (postId) => api.post(`/posts/${postId}/like`),
  getUserPosts: (userId, page = 1, perPage = 10) => 
    api.get(`/posts/user/${userId}`, { params: { page, per_page: perPage } }),
};

export default api;

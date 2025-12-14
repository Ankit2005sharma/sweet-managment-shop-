import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const user = localStorage.getItem('user');
    if (user) {
      const userData = JSON.parse(user);
      if (userData.token) {
        config.headers.Authorization = `Bearer ${userData.token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth APIs
export const registerUser = async (userData) => {
  const response = await api.post('/auth/register/', {
    email: userData.email,
    username: userData.email.split('@')[0], // Use email prefix as username
    first_name: userData.name,
    password: userData.password,
    role: userData.role
  });
  return response.data;
};

export const loginUser = async (credentials) => {
  const response = await api.post('/auth/login/', credentials);
  return response.data;
};

// Sweet APIs
export const getAllSweets = async () => {
  const response = await api.get('/sweets/');
  return response.data;
};

export const getSweetById = async (id) => {
  const response = await api.get(`/sweets/${id}/`);
  return response.data;
};

export const createSweet = async (sweetData) => {
  const response = await api.post('/sweets/', sweetData);
  return response.data;
};

export const updateSweet = async (id, sweetData) => {
  const response = await api.put(`/sweets/${id}/`, sweetData);
  return response.data;
};

export const deleteSweet = async (id) => {
  const response = await api.delete(`/sweets/${id}/`);
  return response.data;
};

export const searchSweets = async (params) => {
  const response = await api.get('/sweets/search/', { params });
  return response.data;
};

// Purchase & Restock APIs
export const purchaseSweet = async (sweetId, quantity = 1) => {
  const response = await api.post(`/sweets/${sweetId}/purchase/`, { quantity });
  return response.data;
};

export const restockSweet = async (sweetId, quantity) => {
  const response = await api.post(`/sweets/${sweetId}/restock/`, { quantity });
  return response.data;
};

// Orders API
export const getMyOrders = async () => {
  const response = await api.get('/orders/my/');
  return response.data;
};

export default api;
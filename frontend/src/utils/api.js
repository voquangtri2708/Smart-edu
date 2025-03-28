import axios from 'axios';

// Create instance of axios with base URL
const api = axios.create({
  baseURL: 'http://localhost:5000/api'
});

// Add request interceptor to include JWT token in headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Không tự động đăng xuất và chuyển hướng khi gặp lỗi 401
    // Người dùng sẽ phải đăng xuất thủ công
    return Promise.reject(error);
  }
);

export default api;

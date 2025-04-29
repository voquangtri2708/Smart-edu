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

// Schedule API module
export const scheduleAPI = {
  // Lấy danh sách lịch học
  getSchedules: (page = 1, per_page = 10, filters = {}) => {
    let url = `/schedules?page=${page}&per_page=${per_page}`;
    
    // Thêm các filter vào URL
    for (const key in filters) {
      if (filters[key]) {
        url += `&${key}=${filters[key]}`;
      }
    }
    
    return api.get(url);
  },
  
  // Lấy chi tiết lịch học theo ID
  getScheduleById: (id) => {
    return api.get(`/schedules/${id}`);
  },
  
  // Tạo lịch học mới
  createSchedule: (data) => {
    return api.post('/schedules', data);
  },
  
  // Cập nhật lịch học
  updateSchedule: (id, data) => {
    return api.put(`/schedules/${id}`, data);
  },
  
  // Xóa lịch học
  deleteSchedule: (id) => {
    return api.delete(`/schedules/${id}`);
  },
  
  // Lấy danh sách lớp học 
  getClasses: () => {
    return api.get('/classes?per_page=200');
  },
  
  // Lấy danh sách phòng học
  getClassrooms: () => {
    return api.get('/classrooms?per_page=200');
  },
  
  // Lấy danh sách môn học
  getSubjects: () => {
    return api.get('/subjects?per_page=200');
  },
  
  // Lấy danh sách tòa nhà
  getBuildings: () => {
    return api.get('/buildings?per_page=200');
  },
  
  // Lấy danh sách cơ sở
  getCampuses: () => {
    return api.get('/campuses?per_page=200');
  }
};

export default api;

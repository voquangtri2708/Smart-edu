import axios from 'axios';

// Tạo instance của axios với base URL
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor: gắn token vào request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor: xử lý lỗi response
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        console.warn('Lỗi xác thực! Vui lòng kiểm tra lại token.');
      }
      if (error.response.status === 403) {
        console.error('Bạn không có quyền thực hiện thao tác này.');
      }
      if (error.response.status >= 500) {
        console.error('Lỗi hệ thống, vui lòng thử lại sau.');
      }
    }
    return Promise.reject(error);
  }
);

// 📌 API: Lịch học
const scheduleAPI = {
  getSchedules: () => api.get('/schedules'),
  getScheduleById: (id) => api.get(`/schedules/${id}`),
  createSchedule: (data) => api.post('/schedules', data),
  updateSchedule: (id, data) => api.put(`/schedules/${id}`, data),
  deleteSchedule: (id) => api.delete(`/schedules/${id}`),
  getSchedulesByClass: (classId) => api.get(`/schedules/class/${classId}`),
  getSchedulesByClassroom: (classroomId) => api.get(`/schedules/classroom/${classroomId}`),
  getSchedulesWithFilters: (params) => api.get('/schedules', { params }),
};

// 📌 API: Phân công giảng dạy
const classTeacherAPI = {
  getClassTeachers: (classId) => api.get(`/classes/${classId}/teachers`),
  assignTeacher: (data) => api.post('/class-teachers', data),
  removeAssignment: (id) => api.delete(`/class-teachers/${id}`),
  getTeacherClasses: (teacherId) => api.get(`/teachers/${teacherId}/classes`),
};

// ✅ 📌 API: Quản lý lớp học
const classAPI = {
  // Lấy danh sách lớp học
  getClasses: (params) => api.get('/classes', { params }),

  // Lấy thông tin lớp học theo ID
  getClassById: (id) => api.get(`/classes/${id}`),

  // Tạo lớp học mới
  createClass: (data) => api.post('/classes', data),

  // Cập nhật lớp học
  updateClass: (id, data) => api.put(`/classes/${id}`, data),

  // Xóa lớp học
  deleteClass: (id) => api.delete(`/classes/${id}`),
};

export { api, scheduleAPI, classTeacherAPI, classAPI };

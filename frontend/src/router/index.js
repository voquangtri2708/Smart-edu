import { createRouter, createWebHistory } from 'vue-router';

// Views thông thường
import Login from '../views/LoginView.vue';
import HomePageView from '@/views/HomePageView.vue';
import StudentFeedback from '@/views/StudentFeedback.vue';
import AdminFeedbackManagement from '@/views/AdminFeedbackManagement.vue';

// Lazy loading các trang quản trị và profile
const AdminStudentManagement = () => import('@/views/admin/StudentManagement.vue');
const AdminTeacherManagement = () => import('@/views/admin/TeacherManagement.vue');
const StudentProfile = () => import('@/views/profile/StudentProfile.vue');
const TeacherProfile = () => import('@/views/profile/TeacherProfile.vue');

// Quản lý lịch học
const ScheduleManagement = () => import('@/views/admin/ScheduleManagement.vue');

// ✅ Quản lý lớp học
const ClassManagement = () => import('@/views/admin/ClassManagement.vue');

const routes = [
  { path: "/", component: HomePageView },
  { path: "/login", component: Login },
  { path: "/student-feedbacks", component: StudentFeedback },
  { path: "/admin-feedback-management", component: AdminFeedbackManagement },

  // Admin routes
  {
    path: "/admin/students",
    component: AdminStudentManagement,
    meta: { requiresAdmin: true }
  },
  {
    path: "/admin/teachers",
    component: AdminTeacherManagement,
    meta: { requiresAdmin: true }
  },

  // Profile routes
  {
    path: "/profile/student",
    component: StudentProfile,
    meta: { requiresStudent: true }
  },
  {
    path: "/profile/teacher",
    component: TeacherProfile,
    meta: { requiresTeacher: true }
  },

  // Quản lý lịch học
  {
    path: "/schedule-management",
    component: ScheduleManagement,
    meta: { requiresTeacher: true }
  },
  {
    path: "/admin/schedule-management",
    name: "ScheduleManagement",
    component: ScheduleManagement
  },

  // ✅ Route mới cho quản lý lớp học
  {
    path: "/admin/class-management",
    name: "ClassManagement",
    component: ClassManagement,
    meta: { requiresTeacher: true } // Hoặc đổi thành requiresAdmin nếu cần
  },

  // Redirect cho profile
  {
    path: "/profile",
    redirect: to => {
      const userRole = localStorage.getItem('user_role');
      if (userRole === 'student') return '/profile/student';
      if (userRole === 'teacher') return '/profile/teacher';
      return '/';
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 📌 Kiểm tra quyền truy cập
router.beforeEach((to, from, next) => {
  const userRole = localStorage.getItem("user_role");

  // Chưa đăng nhập
  if (!userRole && to.path !== "/login") {
    next("/login");
    return;
  }

  // Đã đăng nhập mà truy cập login
  if (userRole && to.path === "/login") {
    next("/");
    return;
  }

  // Kiểm tra quyền hạn
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/');
    return;
  }

  if (to.meta.requiresStudent && userRole !== 'student') {
    next('/');
    return;
  }

  if (to.meta.requiresTeacher && userRole !== 'teacher') {
    next('/');
    return;
  }

  next();
});

export default router;

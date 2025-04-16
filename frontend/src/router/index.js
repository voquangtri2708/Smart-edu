import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/LoginView.vue';
import HomePageView from '@/views/HomePageView.vue';
import StudentFeedback from '@/views/StudentFeedback.vue';
import AdminFeedbackManagement from '@/views/AdminFeedbackManagement.vue';
import SubjectManagement from '../views/admin/SubjectManagement.vue';
import SubjectList from '../views/subject/SubjectList.vue';

// Lazy loading các trang quản lý 
const AdminStudentManagement = () => import('@/views/admin/StudentManagement.vue');
const AdminTeacherManagement = () => import('@/views/admin/TeacherManagement.vue');
const AdminClassManagement = () => import('@/views/admin/ClassManagement.vue');
const StudentProfile = () => import('@/views/profile/StudentProfile.vue');
const TeacherProfile = () => import('@/views/profile/TeacherProfile.vue');

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
  { 
    path: "/admin/subjects", 
    name: "admin-subjects",
    component: SubjectManagement,
    meta: { 
      requiresAuth: true, 
      requiredRole: "admin" 
    }
  },
  { 
    path: "/admin/classes", 
    name: "admin-classes",
    component: AdminClassManagement,
    meta: { 
      requiresAuth: true, 
      requiredRole: "admin" 
    }
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
  // Thêm route redirect cho /profile
  {
    path: "/profile",
    redirect: to => {
      const userRole = localStorage.getItem('user_role');
      if (userRole === 'student') return '/profile/student';
      if (userRole === 'teacher') return '/profile/teacher';
      return '/';
    }
  },
  
  // General Subject List Route
  { 
    path: "/subjects", 
    name: "subjects",
    component: SubjectList,
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const userRole = localStorage.getItem("user_role");

  // Chưa đăng nhập thì chuyển hướng đến trang login
  if (!userRole && to.path !== "/login") {
    next("/login");
    return;
  } 
  
  // Đã đăng nhập mà cố vào trang login thì chuyển về trang chủ
  if (userRole && to.path === "/login") {
    next("/"); 
    return;
  }
  
  // Kiểm tra quyền truy cập
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/'); // Chuyển về trang chủ nếu không phải admin
    return;
  }
  
  if (to.meta.requiresStudent && userRole !== 'student') {
    next('/'); // Chuyển về trang chủ nếu không phải student
    return;
  }
  
  if (to.meta.requiresTeacher && userRole !== 'teacher') {
    next('/'); // Chuyển về trang chủ nếu không phải teacher
    return;
  }
  
  next(); // Cho phép truy cập
});

export default router;
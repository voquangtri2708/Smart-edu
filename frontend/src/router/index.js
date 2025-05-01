import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/LoginView.vue';
import HomePageView from '@/views/HomePageView.vue';
import StudentFeedback from '@/views/StudentFeedback.vue';
import AdminFeedbackManagement from '@/views/admin/FeedbackManagement.vue';
import SubjectManagement from '../views/admin/SubjectManagement.vue';
import CampusManagement from '@/views/admin/CampusManagement.vue';
import ScheduleManagement from '@/views/admin/ScheduleManagement.vue';

// New import for ClassroomManagement
import ClassroomManagement from '@/views/admin/ClassroomManagement.vue';

// New imports for building and classroom management
import BuildingManagement from '@/views/admin/BuildingManagement.vue';

// Lazy loading các trang quản lý 
const AdminStudentManagement = () => import('@/views/admin/StudentManagement.vue');
const AdminTeacherManagement = () => import('@/views/admin/TeacherManagement.vue');
const AdminClassManagement = () => import('@/views/admin/ClassManagement.vue');
const AdminClassStudentsManagement = () => import('@/views/admin/ClassStudentsManagement.vue');
const AdminClassTeachersManagement = () => import('@/views/admin/ClassTeachersManagement.vue');
const StudentProfile = () => import('@/views/profile/StudentProfile.vue');
const TeacherProfile = () => import('@/views/profile/TeacherProfile.vue');

const routes = [
  { path: "/", component: HomePageView },
  { path: "/login", component: Login },
  { path: "/student-feedbacks", component: StudentFeedback },
  { path: "/feedbacks", component: AdminFeedbackManagement },
  
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
  {
    path: '/admin/class-students/:id',
    name: 'admin-class-students-management',
    component: AdminClassStudentsManagement,
    props: true
  },
  {
    path: '/admin/class-teachers/:id',
    name: 'admin-class-teachers-management',
    component: AdminClassTeachersManagement,
    props: true
  },
  {
    path: '/admin/feedbacks',
    name: 'admin-feedback-management',
    component: AdminFeedbackManagement
  },
  {
    path: '/admin/campuses',
    name: 'admin-campus-management',
    component: CampusManagement,
    meta: { 
      requiresAuth: true, 
      requiredRole: "admin" 
    }
  },
  {
    path: '/admin/schedules',
    name: 'admin-schedule-management',
    component: ScheduleManagement,
    meta: { 
      requiresAuth: true, 
      requiredRole: "admin" 
    }
  },

  // Add route for building management
  {
    path: '/admin/campuses/:campusId/buildings',
    name: 'building-management',
    component: BuildingManagement,
    props: true,
    meta: { 
      requiresAuth: true, 
      requiredRole: "admin" 
    }
  },

  // Route for classroom management
  {
    path: '/admin/buildings/:buildingId/classrooms',
    name: 'classroom-management',
    component: ClassroomManagement,
    props: true,
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
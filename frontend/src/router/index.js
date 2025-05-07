import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/LoginView.vue';
import HomePageView from '@/views/HomePageView.vue';
import StudentFeedback from '@/views/student/StudentFeedback.vue';
import AdminFeedbackManagement from '@/views/admin/FeedbackManagement.vue';
import AdminFeedbackStats from '@/views/admin/FeedbackStats.vue';
import SubjectManagement from '../views/admin/SubjectManagement.vue';
import CampusManagement from '@/views/admin/CampusManagement.vue';
import ScheduleManagement from '@/views/admin/ScheduleManagement.vue';
import StudentScheduleView from '@/views/student/StudentScheduleView.vue';
import TeacherScheduleView from '@/views/teacher/TeacherScheduleView.vue';
import QuestionBankManagement from '@/views/admin/QuestionBankManagement.vue';
import TeacherQuestionBankManagement from '@/views/teacher/QuestionBankManagement.vue';
import TeacherExamManagement from '@/views/teacher/ExamManagement.vue';
import ExamQuestionManager from '@/views/teacher/ExamQuestionManager.vue';
import StudentExamView from '@/views/student/StudentExamView.vue';
import StudentExamTakeView from '@/views/student/StudentExamTakeView.vue';
import StudentExamResultView from '@/views/student/StudentExamResultView.vue';
import TeacherExamGradingView from '@/views/teacher/TeacherExamGradingView.vue';

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

// New import for GradeTypeManagement
import GradeTypeManagement from '@/views/admin/GradeTypeManagement.vue';

const routes = [
  { path: "/", component: HomePageView },
  { path: "/login", component: Login },
  { path: "/student-feedbacks", component: StudentFeedback },
  { path: "/feedbacks", component: AdminFeedbackManagement },
  
  // Temporary route to fix the subjects link
  {
    path: "/subjects",
    name: "subjects-redirect",
    redirect: to => {
      const userRole = localStorage.getItem('user_role');
      if (userRole === 'admin') return '/admin/subjects';
      if (userRole === 'student') return '/student/schedule';
      if (userRole === 'teacher') return '/teacher/schedule';
      return '/';
    }
  },
  
  // Student routes
  {
    path: "/student/schedule",
    name: "student-schedule",
    component: StudentScheduleView,
    meta: { 
      requiresAuth: true, 
      requiredRole: "student" 
    }
  },
  {
    path: "/student/exams",
    name: "student-exam-schedule",
    component: StudentExamView,
    meta: { 
      requiresAuth: true, 
      requiredRole: "student" 
    }
  },
  {
    path: "/student/exams/:id/take",
    name: "student-exam-take",
    component: StudentExamTakeView,
    props: true,
    meta: { 
      requiresAuth: true, 
      requiredRole: "student" 
    }
  },
  {
    path: "/student/exams/:id/result",
    name: "student-exam-result",
    component: StudentExamResultView,
    props: true,
    meta: { 
      requiresAuth: true, 
      requiredRole: "student" 
    }
  },
  
  // Teacher routes
  {
    path: "/teacher/schedule",
    name: "teacher-schedule",
    component: TeacherScheduleView,
    meta: { 
      requiresAuth: true, 
      requiredRole: "teacher" 
    }
  },
  {
    path: "/teacher/questions",
    name: "teacher-question-bank",
    component: TeacherQuestionBankManagement,
    meta: { 
      requiresAuth: true, 
      requiredRole: "teacher" 
    }
  },
  {
    path: "/teacher/exams",
    name: "teacher-exams",
    component: TeacherExamManagement,
    meta: { 
      requiresAuth: true, 
      requiredRole: "teacher" 
    }
  },
  {
    path: "/teacher/exams/:examId/questions",
    name: "exam-questions",
    component: ExamQuestionManager,
    props: true,
    meta: { 
      requiresAuth: true, 
      requiredRole: "teacher" 
    }
  },
  {
    path: "/teacher/exams/:examId/grading",
    name: "exam-grading",
    component: TeacherExamGradingView,
    props: true,
    meta: { 
      requiresAuth: true, 
      requiredRole: "teacher" 
    }
  },
  {
    path: "/teacher/exams/grading",
    name: "exams-grading-list",
    component: () => import('@/views/teacher/TeacherExamsGradingList.vue'),
    meta: { 
      requiresAuth: true, 
      requiredRole: "teacher" 
    }
  },
  
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
    path: "/admin/questions",
    name: "admin-question-bank",
    component: QuestionBankManagement,
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
    path: '/admin/stats/feedback',
    name: 'admin-feedback-stats',
    component: AdminFeedbackStats,
    meta: { 
      requiresAuth: true, 
      requiredRole: "admin" 
    }
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
  // Question Bank redirect based on role
  {
    path: "/questions",
    redirect: to => {
      const userRole = localStorage.getItem('user_role');
      if (userRole === 'admin') return '/admin/questions';
      if (userRole === 'teacher') return '/teacher/questions';
      return '/';
    }
  },
  // Exam redirect based on role
  {
    path: "/exams",
    redirect: to => {
      const userRole = localStorage.getItem('user_role');
      if (userRole === 'teacher') return '/teacher/exams';
      return '/';
    }
  },
  {
    path: '/admin/grade-types',
    name: 'admin-grade-types',
    component: GradeTypeManagement,
    meta: {
      requiresAuth: true,
      requiredRole: 'admin'
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
import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/LoginView.vue';
import HomePageView from '@/views/HomePageView.vue';
import InstructorFeedbackView from '@/views/InstructorFeedbackView.vue';
import ClassroomFeedbackView from '@/views/ClassroomFeedbackView.vue';

const routes = [
  { path: "/", component: HomePageView },
  { path: "/login", component: Login },
  { path: "/instructor-feedbacks", component: InstructorFeedbackView },
  { path: "/classroom-feedbacks", component: ClassroomFeedbackView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem("user_role"); 

  if (!isLoggedIn && to.path !== "/login") {
    next("/login");
  } else if (isLoggedIn && to.path === "/login") {
    next("/"); 
  } else {
    next(); 
  }
});

export default router;

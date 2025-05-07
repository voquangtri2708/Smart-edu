<template>
  <div class="sidebar" :class="{ 'hidden': !isExpanded }">
    <div class="sidebar-inner">
      <!-- Nếu là Student -->
      <div v-if="role === 'student'" class="sidebar-section">
        <div class="section-title">
          <i class="bi bi-mortarboard me-2"></i>Học tập
        </div>
        
        <div class="menu-item" @click="toggleMenu('study')">
          <div class="menu-item-content">
            <i class="bi bi-book me-2"></i>
            <span>Học tập</span>
          </div>
          <i :class="getIconClass('study')"></i>
        </div>
        
        <div v-if="menuOpen.study" class="submenu">
          <router-link to="/subjects" class="submenu-item" active-class="active">
            <i class="bi bi-journal-bookmark me-2"></i>Danh sách môn học
          </router-link>
          <router-link to="/student/schedule" class="submenu-item" active-class="active">
            <i class="bi bi-calendar3 me-2"></i>Lịch học
          </router-link>
          <router-link to="/student/exams" class="submenu-item" active-class="active">
            <i class="bi bi-journal-check me-2"></i>Lịch kiểm tra
          </router-link>
          <router-link to="/student/grades" class="submenu-item" active-class="active">
            <i class="bi bi-table me-2"></i>Bảng điểm
          </router-link>
        </div>

        <div class="menu-item" @click="toggleMenu('survey')">
          <div class="menu-item-content">
            <i class="bi bi-star me-2"></i>
            <span>Đánh giá & Khảo sát</span>
          </div>
          <i :class="getIconClass('survey')"></i>
        </div>
        
        <div v-if="menuOpen.survey" class="submenu">
          <router-link to="/student-feedbacks" class="submenu-item" active-class="active">
            <i class="bi bi-chat-square-text me-2"></i>Đánh giá và khảo sát
          </router-link>
        </div>
        
        <!-- Thêm mới: Thông tin cá nhân -->
        <div class="menu-item" @click="toggleMenu('profile')">
          <div class="menu-item-content">
            <i class="bi bi-person me-2"></i>
            <span>Thông tin cá nhân</span>
          </div>
          <i :class="getIconClass('profile')"></i>
        </div>
        
        <div v-if="menuOpen.profile" class="submenu">
          <router-link to="/profile/student" class="submenu-item" active-class="active">
            <i class="bi bi-person-vcard me-2"></i>Hồ sơ sinh viên
          </router-link>
        </div>
      </div>

      <!-- Nếu là Teacher -->
      <div v-if="role === 'teacher'" class="sidebar-section">
        <div class="section-title">
          <i class="bi bi-person-badge me-2"></i>Giảng dạy
        </div>
        
        <div class="menu-item" @click="toggleMenu('teaching')">
          <div class="menu-item-content">
            <i class="bi bi-easel2 me-2"></i>
            <span>Giảng dạy</span>
          </div>
          <i :class="getIconClass('teaching')"></i>
        </div>
        
        <div v-if="menuOpen.teaching" class="submenu">
          <router-link to="/subjects" class="submenu-item" active-class="active">
            <i class="bi bi-journal-bookmark me-2"></i>Danh sách môn học
          </router-link>
          <router-link to="/teacher/schedule" class="submenu-item" active-class="active">
            <i class="bi bi-calendar3-week me-2"></i>Lịch dạy
          </router-link>
          <router-link to="/teacher/grade-entry" class="submenu-item" active-class="active">
            <i class="bi bi-pencil-square me-2"></i>Nhập điểm sinh viên
          </router-link>
          <router-link to="/teacher/questions" class="submenu-item" active-class="active">
            <i class="bi bi-question-circle me-2"></i>Ngân hàng câu hỏi
          </router-link>
          <router-link to="/teacher/exams" class="submenu-item" active-class="active">
            <i class="bi bi-file-earmark-text me-2"></i>Quản lý đợt thi
          </router-link>
          <router-link to="/teacher/exams/grading" class="submenu-item" active-class="active">
            <i class="bi bi-check-square me-2"></i>Chấm điểm bài thi
          </router-link>
        </div>
        
        <!-- Thêm mới: Thông tin cá nhân -->
        <div class="menu-item" @click="toggleMenu('profile')">
          <div class="menu-item-content">
            <i class="bi bi-person me-2"></i>
            <span>Thông tin cá nhân</span>
          </div>
          <i :class="getIconClass('profile')"></i>
        </div>
        
        <div v-if="menuOpen.profile" class="submenu">
          <router-link to="/profile/teacher" class="submenu-item" active-class="active">
            <i class="bi bi-person-vcard me-2"></i>Hồ sơ giảng viên
          </router-link>
        </div>
      </div>

      <!-- Nếu là Admin -->
      <div v-if="role === 'admin'" class="sidebar-section">
        <div class="section-title">
          <i class="bi bi-gear me-2"></i>Quản lý hệ thống
        </div>
        <!-- Thêm mới: Quản lý người dùng -->
        <div class="menu-item" @click="toggleMenu('users')">
          <div class="menu-item-content">
            <i class="bi bi-people me-2"></i>
            <span>Quản lý người dùng</span>
          </div>
          <i :class="getIconClass('users')"></i>
        </div>
        
        <div v-if="menuOpen.users" class="submenu">
          <router-link to="/admin/students" class="submenu-item" active-class="active">
            <i class="bi bi-mortarboard me-2"></i>Quản lý sinh viên
          </router-link>
          <router-link to="/admin/teachers" class="submenu-item" active-class="active">
            <i class="bi bi-person-badge me-2"></i>Quản lý giảng viên
          </router-link>
        </div>
        <div class="menu-item" @click="toggleMenu('management')">
          <div class="menu-item-content">
            <i class="bi bi-bar-chart-line me-2"></i>
            <span>Quản lý đánh giá</span>
          </div>
          <i :class="getIconClass('management')"></i>
        </div>
        
        <div v-if="menuOpen.management" class="submenu">
          <router-link to="/feedbacks" class="submenu-item" active-class="active">
            <i class="bi bi-clipboard-data me-2"></i>Quản lý đánh giá
          </router-link>
          <router-link to="/admin/stats/feedback" class="submenu-item" active-class="active">
            <i class="bi bi-bar-chart me-2"></i>Báo cáo và thống kê đánh giá
          </router-link>
        </div>
        
        <!-- Quản lý chương trình học -->
        <div class="menu-item" @click="toggleMenu('curriculum')">
          <div class="menu-item-content">
            <i class="bi bi-journal-text me-2"></i>
            <span>Quản lý chương trình học</span>
          </div>
          <i :class="getIconClass('curriculum')"></i>
        </div>
        
        <div v-if="menuOpen.curriculum" class="submenu">
          <router-link to="/admin/subjects" class="submenu-item" active-class="active">
            <i class="bi bi-journal-bookmark me-2"></i>Quản lý môn học
          </router-link>
          <router-link to="/admin/classes" class="submenu-item" active-class="active">
            <i class="bi bi-calendar3 me-2"></i>Quản lý lớp học
          </router-link>
          <router-link to="/admin/schedules" class="submenu-item" active-class="active">
            <i class="bi bi-clock me-2"></i>Quản lý lịch học
          </router-link>
          <router-link to="/admin/questions" class="submenu-item" active-class="active">
            <i class="bi bi-question-circle me-2"></i>Ngân hàng câu hỏi
          </router-link>
          <router-link to="/admin/grade-types" class="submenu-item" active-class="active">
            <i class="bi bi-percent me-2"></i>Quản lý loại điểm
          </router-link>
        </div>
        
        <!-- Thêm mới: Quản lý cơ sở vật chất -->
        <div class="menu-item" @click="toggleMenu('campuses')">
          <div class="menu-item-content">
            <i class="bi bi-building me-2"></i>
            <span>Quản lý cơ sở vật chất</span>
          </div>
          <i :class="getIconClass('facilities')"></i>
        </div>
        
        <div v-if="menuOpen.campuses" class="submenu">
          <router-link to="/admin/campuses" class="submenu-item" active-class="active">
            <i class="bi bi-geo-alt me-2"></i>Quản lý cơ sở
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute } from 'vue-router';

// Biến lưu role người dùng
const role = ref("");
const isExpanded = ref(true);
const route = useRoute();

// Trạng thái mở menu
const menuOpen = ref({
  study: false,
  survey: false,
  teaching: false,
  management: false,
  users: false,
  profile: false,
  curriculum: false,
  facilities: false,
});

// Lấy role từ localStorage khi component được mount
onMounted(() => {
  role.value = localStorage.getItem("user_role") || "student";
  
  // Mở menu dựa vào route hiện tại
  highlightActiveMenu();
  
  // Kiểm tra trạng thái sidebar từ localStorage
  const savedState = localStorage.getItem("sidebar_expanded");
  if (savedState !== null) {
    isExpanded.value = savedState === "true";
  }
});

// Theo dõi thay đổi route để highlight menu tương ứng
watch(() => route.path, () => {
  highlightActiveMenu();
});

// Highlight menu đang active
const highlightActiveMenu = () => {
  const path = route.path;
  
  // Reset tất cả
  Object.keys(menuOpen.value).forEach(key => {
    menuOpen.value[key] = false;
  });
  
  // Mở menu phù hợp với route hiện tại
  if (path.includes('student-feedbacks')) {
    menuOpen.value.survey = true;
  } else if (path.includes('feedbacks') || path.includes('admin/stats/feedback')) {
    menuOpen.value.management = true;
  } else if (path.includes('admin/students')) {
    menuOpen.value.users = true;
  } else if (path.includes('admin/teachers')) {
    menuOpen.value.users = true;
  } else if (path.includes('admin/subjects')) {
    menuOpen.value.curriculum = true;
  } else if (path.includes('admin/classes')) {
    menuOpen.value.curriculum = true;
  } else if (path.includes('admin/campuses')) {
    menuOpen.value.campuses = true;
  } else if (path.includes('profile/student')) {
    menuOpen.value.profile = true;
  } else if (path.includes('profile/teacher')) {
    menuOpen.value.profile = true;
  } else if (path.includes('/subjects')) {
    menuOpen.value.study = true;
  } else if (path.includes('student/schedule')) {
    menuOpen.value.study = true;
  } else if (path.includes('student/grades')) {
    menuOpen.value.study = true;
  } else if (path.includes('student/exams')) {
    menuOpen.value.study = true;
  } else if (path.includes('teacher/schedule')) {
    menuOpen.value.teaching = true;
  } else if (path.includes('teacher/grade-entry')) {
    menuOpen.value.teaching = true;
  } else if (path.includes('teacher/questions')) {
    menuOpen.value.teaching = true;
  } else if (path.includes('teacher/exams')) {
    menuOpen.value.teaching = true;
  }
};

// Toggle menu
const toggleMenu = (menu) => {
  menuOpen.value[menu] = !menuOpen.value[menu];
};

// Trả về icon class tương ứng
const getIconClass = (menu) => {
  return menuOpen.value[menu] ? "bi bi-chevron-down" : "bi bi-chevron-right";
};
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 70px; /* Khoảng trống bằng chiều cao navbar */
  left: 0;
  width: 280px;
  height: calc(100vh - 70px); /* Chiều cao trừ đi chiều cao navbar */
  background: white;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
  transition: transform 0.3s ease, width 0.3s ease;
  z-index: 100;
  border-right: 1px solid rgba(0, 0, 0, 0.08);
}

.sidebar.hidden {
  transform: translateX(-280px);
}

.sidebar-inner {
  padding: 15px 0;
}

.sidebar-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: #777;
  padding: 10px 20px;
  letter-spacing: 1px;
}

/* Menu chính */
.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  border-left: 3px solid transparent;
}

.menu-item-content {
  display: flex;
  align-items: center;
}

.menu-item:hover {
  background-color: rgba(13, 110, 253, 0.05);
  border-left-color: #0d6efd;
}

/* Submenu */
.submenu {
  margin: 5px 0;
  padding-left: 20px;
}

.submenu-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  color: #555;
  text-decoration: none;
  font-size: 0.95rem;
  border-radius: 4px;
  transition: all 0.2s;
  margin: 2px 0;
}

.submenu-item:hover {
  background-color: rgba(13, 110, 253, 0.05);
  color: #0d6efd;
}

.submenu-item.active {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  font-weight: 500;
}

/* Icons */
.bi {
  font-size: 1rem;
}

/* Scrollbar styles */
.sidebar::-webkit-scrollbar {
  width: 5px;
}

.sidebar::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}

.sidebar::-webkit-scrollbar-track {
  background-color: rgba(0, 0, 0, 0.05);
}

/* Responsive */
@media screen and (max-width: 768px) {
  .sidebar {
    display: none;
  }
}
</style>
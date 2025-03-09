<template>
    <div class="sidebar">
      <!-- Nếu là Student -->
      <div v-if="role === 'student'">
        <div class="menu-item" @click="toggleMenu('study')">
          Học tập <i :class="getIconClass('study')"></i>
        </div>
        <ul v-if="menuOpen.study" class="submenu">
          <li><a href="#">Lịch học</a></li>
          <li><a href="#">Bảng điểm</a></li>
        </ul>
  
        <div class="menu-item" @click="toggleMenu('survey')">
          Đánh giá & Khảo sát <i :class="getIconClass('survey')"></i>
        </div>
        <ul v-if="menuOpen.survey" class="submenu">
          <li><a href="#">Đánh giá giảng viên</a></li>
          <li><a href="#">Đánh giá phòng học</a></li>
        </ul>
      </div>
  
      <!-- Nếu là Teacher -->
      <div v-if="role === 'teacher'">
        <div class="menu-item" @click="toggleMenu('teaching')">
          Giảng dạy <i :class="getIconClass('teaching')"></i>
        </div>
        <ul v-if="menuOpen.teaching" class="submenu">
          <li><a href="#">Lịch dạy</a></li>
          <li><a href="#">Nhập điểm sinh viên</a></li>
        </ul>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  
  // Giả lập role, có thể lấy từ Vuex/Pinia hoặc API
  const role = ref("");
  
  // Trạng thái mở menu
  const menuOpen = ref({
    study: false,
    survey: false,
    teaching: false,
  });
  
  // Lấy role từ localStorage khi component được mount
  onMounted(() => {
    role.value = localStorage.getItem("user_role") || "student"; // Mặc định là "student" nếu không có role
  });
  
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
    top: 80px; /* Khoảng trống bằng chiều cao navbar */
    left: 0;
    width: 280px;
    height: calc(100vh - 80px); /* Chiều cao trừ đi chiều cao navbar */
    background: white;
    padding: 15px;
    box-shadow: 4px 0 6px rgba(0, 0, 0, 0.1);
    overflow-y: auto;
    transition: transform 0.3s ease-in-out;
  }
  
  .sidebar.hidden {
    transform: translateX(-100%);
  }
  
  /* Menu chính */
  .menu-item {
    font-size: 16px;
    font-weight: bold;
    padding: 10px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #ddd;
    word-wrap: break-word; /* Thêm thuộc tính này */
    white-space: normal; /* Thêm thuộc tính này */
  }
  
  .menu-item:hover {
    background: #f0f0f0;
  }
  
  /* Submenu */
  .submenu {
    list-style: none;
    padding: 0;
    margin-left: 15px;
  }
  
  .submenu li {
    padding: 8px 0;
  }
  
  .submenu li a {
    text-decoration: none;
    color: #333;
    font-size: 14px;
    word-wrap: break-word; /* Thêm thuộc tính này */
    white-space: normal; /* Thêm thuộc tính này */
  }
  
  .submenu li a:hover {
    color: #007bff;
  }
  
  /* Biểu tượng */
  .bi {
    font-size: 14px;
  }
  
  @media screen and (max-width: 768px) {
    .sidebar {
      display: none;
    }
  }
  </style>
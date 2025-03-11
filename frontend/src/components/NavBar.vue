<template>
  <nav :class="{ 'scrolled': isScrolled }" class="navbar">
    <div class="container-fluid">
      <!-- Icon ẩn/hiện sidebar -->
      <button class="sidebar-toggle-btn" @click="toggleSidebar">
        <i :class="isSidebarOpen ? 'bi bi-x' : 'bi bi-list'"></i>
      </button>

      <!-- Logo ở giữa -->
      <div class="navbar-logo mx-auto">
        <a class="navbar-brand" href="/">
          <img src="/Logo.png" alt="Logo" :class="{ 'logo-small': isScrolled }" />
        </a>
      </div>

      <!-- Profile menu (Ẩn trên màn hình nhỏ) -->
      <div class="profile-menu dropdown d-none d-md-block">
        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
          {{ username }}
        </a>
        <ul class="dropdown-menu dropdown-menu-end">
          <li><a class="dropdown-item" href="/profile">Thông tin cá nhân</a></li>
          <li><button class="dropdown-item" @click="logout">Đăng xuất</button></li>
        </ul>
      </div>

      <!-- Hamburger Menu (Hiện trên màn hình nhỏ) -->
      <div class="hamburger-menu d-md-none">
        <button class="hamburger-btn" @click="toggleMenu">
          ☰
        </button>
        <div v-if="isMenuOpen" class="dropdown-menu show">
          <a class="dropdown-item" href="/profile">Thông tin cá nhân</a>
          <button class="dropdown-item" @click="logout">Đăng xuất</button>

          <hr />

          <!-- Menu cho Student -->
          <template v-if="role === 'student'">
            <div class="dropdown-item" @click="toggleSubmenu('study')">
              Học tập ▾
            </div>
            <div v-if="submenuOpen.study" class="submenu">
              <a class="dropdown-item" href="#">Lịch học</a>
              <a class="dropdown-item" href="#">Bảng điểm</a>
            </div>

            <div class="dropdown-item" @click="toggleSubmenu('feedback')">
              Đánh giá & Khảo sát ▾
            </div>
            <div v-if="submenuOpen.feedback" class="submenu">
              <a class="dropdown-item" href="#">Đánh giá giảng viên</a>
              <a class="dropdown-item" href="#">Đánh giá phòng học</a>
            </div>
          </template>

          <!-- Menu cho Teacher -->
          <template v-if="role === 'teacher'">
            <div class="dropdown-item" @click="toggleSubmenu('teaching')">
              Giảng dạy ▾
            </div>
            <div v-if="submenuOpen.teaching" class="submenu">
              <a class="dropdown-item" href="#">Lịch dạy</a>
              <a class="dropdown-item" href="#">Nhập điểm sinh viên</a>
            </div>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const username = ref("");
const role = ref("student"); // Thay đổi thành "teacher" để test
const isScrolled = ref(false);
const isMenuOpen = ref(false);
const isSidebarOpen = ref(true); // Trạng thái của sidebar
const submenuOpen = ref({
  study: false,
  feedback: false,
  teaching: false,
});

const router = useRouter();

onMounted(() => {
  username.value = localStorage.getItem("username") || "Người dùng";
  window.addEventListener("scroll", handleScroll);
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50;
};

const logout = () => {
  localStorage.removeItem("username");
  localStorage.removeItem("user_role");
  router.push("/login");
};

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};

// Toggle submenu
const toggleSubmenu = (menu) => {
  submenuOpen.value[menu] = !submenuOpen.value[menu];
};

// Toggle sidebar
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
  document.querySelector('.sidebar').classList.toggle('hidden');
  document.querySelector('main').classList.toggle('full-width');
};
</script>

<style scoped>
/* Navbar */
.navbar {
  background-color: white;
  height: 80px;
  padding: 20px 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  transition: all 0.3s ease-in-out;
}

.navbar.scrolled {
  height: 64px;
  padding: 10px 0;
}

/* Logo */
.navbar-logo {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.navbar-logo img {
  height: 70px;
  transition: all 0.3s ease-in-out;
}

.navbar-logo img.logo-small {
  height: 60px;
}

/* Profile menu */
.profile-menu {
  position: absolute;
  right: 50px;
}

/* Hamburger menu */
.hamburger-menu {
  position: absolute;
  right: 20px;
  display: flex;
  align-items: center;
}

.hamburger-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

/* Sidebar toggle button */
.sidebar-toggle-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  position: absolute;
  left: 20px;
}

/* Dropdown menu */
.dropdown-menu {
  position: absolute;
  top: 50px;
  right: 10px;
  background: white;
  border-radius: 5px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: none;
  min-width: 220px;
  word-wrap: break-word; /* Thêm thuộc tính này */
  white-space: normal; /* Thêm thuộc tính này */
}

.dropdown-menu.show {
  display: block;
}

/* Submenu */
.submenu {
  padding-left: 15px;
}

.dropdown-item {
  cursor: pointer;
  word-wrap: break-word; /* Thêm thuộc tính này */
  white-space: normal; /* Thêm thuộc tính này */
}

.dropdown-item:hover {
  background-color: #f1f1f1;
}

/* Ẩn sidebar khi màn hình nhỏ */
@media (max-width: 768px) {
  .sidebar-toggle-btn {
    display: none;
  }
}
</style>
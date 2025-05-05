<template>
  <nav :class="{ 'scrolled': isScrolled, 'shadow-sm': isScrolled }" class="navbar">
    <div class="container-fluid px-md-4">
      <!-- Icon ẩn/hiện sidebar -->
      <button class="sidebar-toggle-btn d-none d-md-flex" @click="toggleSidebar">
        <i :class="isSidebarOpen ? 'bi bi-layout-sidebar-inset' : 'bi bi-layout-sidebar'" class="fs-5"></i>
      </button>

      <!-- Logo ở giữa -->
      <div class="navbar-logo">
        <a class="navbar-brand" href="/">
          <img src="/Logo.png" alt="Logo" :class="{ 'logo-small': isScrolled }" />
        </a>
      </div>

      <!-- Profile menu (Desktop) -->
      <div class="profile-menu d-none d-md-block">
        <div class="dropdown">
          <button 
            class="btn dropdown-toggle user-dropdown" 
            type="button" 
            id="profileDropdown" 
            @click="toggleProfileMenu"
          >
            <div class="d-flex align-items-center">
              <div class="avatar-circle me-2">{{ usernameInitial }}</div>
              <span>{{ username }}</span>
            </div>
          </button>
          <ul class="dropdown-menu dropdown-menu-end shadow-sm" :class="{ 'show': isProfileMenuOpen }">
            <li><h6 class="dropdown-header">{{ getRoleText() }}</h6></li>
            <li v-if="role !== 'admin'"><hr class="dropdown-divider"></li>
            <li v-if="role !== 'admin'"><router-link class="dropdown-item" to="/profile">
              <i class="bi bi-person me-2"></i>Thông tin cá nhân
            </router-link></li>
            <li><hr class="dropdown-divider"></li>
            <li><button class="dropdown-item text-danger" @click="logout">
              <i class="bi bi-box-arrow-right me-2"></i>Đăng xuất
            </button></li>
          </ul>
        </div>
      </div>

      <!-- Hamburger Menu (Mobile) -->
      <div class="mobile-menu d-md-none">
        <button class="btn mobile-menu-btn" @click="toggleMenu">
          <i class="bi" :class="isMenuOpen ? 'bi-x-lg' : 'bi-list'"></i>
        </button>
        <div class="mobile-dropdown" v-if="isMenuOpen">
          <div class="mobile-dropdown-content shadow">
            <!-- User info -->
            <div class="mobile-user-info">
              <div class="avatar-circle">{{ usernameInitial }}</div>
              <div class="ms-3">
                <h6 class="mb-0">{{ username }}</h6>
                <small class="text-muted">{{ getRoleText() }}</small>
              </div>
            </div>
            <hr>

            <!-- Menu cho Student -->
            <template v-if="role === 'student'">
              <div class="mobile-menu-item" @click="toggleSubmenu('study')">
                <div>
                  <i class="bi bi-book me-2"></i>
                  Học tập
                </div>
                <i :class="submenuOpen.study ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
              </div>
              <div v-if="submenuOpen.study" class="mobile-submenu">
                <router-link to="#" class="mobile-submenu-item">Lịch học</router-link>
                <router-link to="#" class="mobile-submenu-item">Bảng điểm</router-link>
              </div>

              <div class="mobile-menu-item" @click="toggleSubmenu('feedback')">
                <div>
                  <i class="bi bi-star me-2"></i>
                  Đánh giá & Khảo sát
                </div>
                <i :class="submenuOpen.feedback ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
              </div>
              <div v-if="submenuOpen.feedback" class="mobile-submenu">
                <router-link to="/student-feedbacks" class="mobile-submenu-item">Đánh giá và khảo sát</router-link>
              </div>
            </template>

            <!-- Menu cho Teacher -->
            <template v-if="role === 'teacher'">
              <div class="mobile-menu-item" @click="toggleSubmenu('teaching')">
                <div>
                  <i class="bi bi-person-video3 me-2"></i>
                  Giảng dạy
                </div>
                <i :class="submenuOpen.teaching ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
              </div>
              <div v-if="submenuOpen.teaching" class="mobile-submenu">
                <router-link to="#" class="mobile-submenu-item">Lịch dạy</router-link>
                <router-link to="#" class="mobile-submenu-item">Nhập điểm sinh viên</router-link>
              </div>
            </template>

            <!-- Menu cho Admin -->
            <template v-if="role === 'admin'">
              <div class="mobile-menu-item" @click="toggleSubmenu('management')">
                <div>
                  <i class="bi bi-gear me-2"></i>
                  Quản lý
                </div>
                <i :class="submenuOpen.management ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
              </div>
              <div v-if="submenuOpen.management" class="mobile-submenu">
                <router-link to="/feedbacks" class="mobile-submenu-item">
                  Quản lý đánh giá
                </router-link>
                <router-link to="/admin/campuses" class="mobile-submenu-item">
                  Quản lý cơ sở vật chất
                </router-link>
              </div>
            </template>

            <hr>
            <!-- Profile & Logout -->
            <router-link to="/profile" class="mobile-menu-item">
              <i class="bi bi-person me-2"></i>Thông tin cá nhân
            </router-link>
            <div class="mobile-menu-item text-danger" @click="logout">
              <i class="bi bi-box-arrow-right me-2"></i>Đăng xuất
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
  <!-- Overlay cho mobile menu -->
  <div v-if="isMenuOpen" class="mobile-overlay" @click="toggleMenu"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useRouter } from "vue-router";

const username = ref("");
const role = ref("");
const isScrolled = ref(false);
const isMenuOpen = ref(false);
const isSidebarOpen = ref(true);
const isProfileMenuOpen = ref(false);
const submenuOpen = ref({
  study: false,
  feedback: false,
  teaching: false,
  management: false
});

const router = useRouter();

// Tính chữ cái đầu của tên người dùng làm avatar
const usernameInitial = computed(() => {
  if (!username.value) return '?';
  return username.value.charAt(0).toUpperCase();
});

// Get role text
const getRoleText = () => {
  switch (role.value) {
    case 'admin': return 'Quản trị viên';
    case 'teacher': return 'Giảng viên';
    case 'student': return 'Sinh viên';
    default: return 'Người dùng';
  }
};

onMounted(() => {
  username.value = localStorage.getItem("username") || "Người dùng";
  role.value = localStorage.getItem("user_role") || "student";
  window.addEventListener("scroll", handleScroll);
  document.addEventListener('click', closeDropdownsOnOutsideClick);
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
  document.removeEventListener('click', closeDropdownsOnOutsideClick);
});

const closeDropdownsOnOutsideClick = (event) => {
  const profileDropdown = document.getElementById('profileDropdown');
  const dropdown = document.querySelector('.dropdown-menu');
  
  if (profileDropdown && !profileDropdown.contains(event.target) && 
      dropdown && !dropdown.contains(event.target)) {
    isProfileMenuOpen.value = false;
  }
};

const handleScroll = () => {
  isScrolled.value = window.scrollY > 10;
};

const logout = () => {
  localStorage.removeItem("auth_token");
  localStorage.removeItem("username");
  localStorage.removeItem("user_role");
  localStorage.removeItem("student_id");
  localStorage.removeItem("teacher_id");
  router.push("/login");
};

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
  if (isMenuOpen.value) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = 'auto';
  }
};

const toggleProfileMenu = () => {
  isProfileMenuOpen.value = !isProfileMenuOpen.value;
};

const toggleSubmenu = (menu) => {
  submenuOpen.value[menu] = !submenuOpen.value[menu];
};

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
  document.querySelector('.sidebar')?.classList.toggle('hidden');
  document.querySelector('main')?.classList.toggle('full-width');
};
</script>

<style scoped>
/* Navbar */
.navbar {
  background-color: white;
  height: 70px;
  padding: 0.5rem 0;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1030; /* Increased z-index to ensure dropdown appears above other elements */
  transition: all 0.3s ease;
}

.navbar.scrolled {
  height: 60px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
}

/* Logo */
.navbar-logo {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.navbar-logo img {
  height: 55px;
  transition: all 0.3s ease;
}

.navbar-logo img.logo-small {
  height: 45px;
}

/* Sidebar toggle button */
.sidebar-toggle-btn {
  background: transparent;
  border: none;
  color: #333;
  border-radius: 4px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.sidebar-toggle-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #0d6efd;
}

/* Profile Menu */
.profile-menu {
  position: absolute;
  right: 20px;
}

.user-dropdown {
  background: transparent;
  border: none;
  padding: 8px 12px;
  border-radius: 30px;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  position: relative; /* Added position relative for proper dropdown positioning */
}

.user-dropdown:hover {
  background: rgba(0, 0, 0, 0.05);
}

.user-dropdown:after {
  margin-left: 8px;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #0d6efd;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
}

/* Dropdown menu styles */
.dropdown-menu {
  border-radius: 8px;
  border: none;
  padding: 8px 0;
  margin-top: 10px;
  min-width: 220px; /* Increased width to accommodate text */
  transition: opacity 0.3s, transform 0.3s;
  z-index: 1035; /* Ensure dropdown is above navbar */
  position: absolute;
  right: 0; /* Align to right side of dropdown toggle */
}

.dropdown-menu.show {
  display: block;
  opacity: 1;
  transform: translateY(0);
}

.dropdown-item {
  padding: 8px 16px;
  font-size: 0.95rem;
  transition: all 0.15s ease;
  white-space: nowrap; /* Prevent text from wrapping */
}

.dropdown-item:hover {
  background-color: rgba(13, 110, 253, 0.08);
}

.dropdown-item.text-danger:hover {
  background-color: rgba(220, 53, 69, 0.08);
}

/* Mobile Menu */
.mobile-menu {
  position: absolute;
  right: 15px;
}

.mobile-menu-btn {
  font-size: 1.3rem;
  padding: 0.25rem 0.5rem;
  color: #333;
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1025; /* Make sure it's below dropdown but above content */
}

.mobile-dropdown {
  position: fixed;
  top: 70px;
  right: 0;
  width: 280px;
  max-height: calc(100vh - 70px);
  overflow-y: auto;
  background: white;
  z-index: 1040; /* Make sure mobile menu is above everything */
  animation: slideIn 0.3s ease forwards;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.mobile-dropdown-content {
  padding: 15px;
}

.mobile-user-info {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.mobile-menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.mobile-menu-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.mobile-submenu {
  padding-left: 15px;
  margin-bottom: 10px;
}

.mobile-submenu-item {
  display: block;
  padding: 10px 15px;
  color: #666;
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.mobile-submenu-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #0d6efd;
}

@media (max-width: 768px) {
  .navbar-logo img {
    height: 45px;
  }
  
  .navbar-logo img.logo-small {
    height: 40px;
  }
  
  .mobile-dropdown {
    width: 100%;
  }
  
  /* Adjust dropdown position on mobile */
  .dropdown-menu {
    position: absolute;
    left: auto;
    right: 0;
    min-width: 200px;
  }
}
</style>
<script setup>
import { useRoute } from 'vue-router';
import { computed } from 'vue';
import { RouterView } from 'vue-router';
import NavBar from './components/NavBar.vue';
import SideBar from './components/Sidebar.vue';

const route = useRoute();

// Kiểm tra nếu route hiện tại là "/login" thì ẩn NavBar & SideBar
const showNavbar = computed(() => route.path !== "/login");
</script>

<template>
  <div>
    <!-- Chỉ hiển thị navbar nếu không phải trang login -->
    <NavBar v-if="showNavbar" />

    <div class="layout">
      <!-- Sidebar (chỉ hiển thị khi không ở trang login) -->
      <SideBar v-if="showNavbar" />

      <!-- Nội dung chính -->
      <main :class="{ 'with-navbar': showNavbar, 'with-sidebar': showNavbar }">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Layout chính chia thành 2 phần */
.layout {
  display: flex;
}

/* Nếu có navbar, thêm khoảng trống bên trên */
.with-navbar {
  padding-top: 80px; /* Khoảng trống bằng chiều cao navbar */
}

/* Nếu có sidebar, tạo khoảng trống bên trái */
.with-sidebar {
  padding-left: 280px; /* Để tránh bị sidebar che mất nội dung */
}

/* Nội dung chính */
main {
  flex-grow: 1;
  padding: 20px;
}

.full-width {
  padding-left: 0 !important;
  width: 100% !important;
}

/* Ẩn sidebar trên màn hình nhỏ */
@media screen and (max-width: 768px) {
  .with-sidebar {
    padding-left: 0;
  }

  .layout {
    flex-direction: column;
  }
}
</style>
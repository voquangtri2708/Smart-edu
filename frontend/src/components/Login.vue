<template>
  <div class="login-container">
    <div class="login-box">
      <img src="/Logo.png" alt="Logo" class="logo" />

      <input v-model="identifier" type="text" placeholder="Tên đăng nhập, Email hoặc số điện thoại" class="input-field" />

      <!-- Trường nhập mật khẩu -->
      <div class="password-container">
        <input 
          :type="showPassword ? 'text' : 'password'" 
          v-model="password" 
          placeholder="Mật khẩu" 
          class="input-field" 
        />
        <i 
          v-if="password.length > 0" 
          :class="showPassword ? 'bi bi-eye' : 'bi bi-eye-slash'" 
          class="toggle-password" 
          @click="togglePassword"
        ></i>
      </div>

      <button @click="login" class="login-button">Đăng nhập</button>

      <div class="forgot-password">
        <a href="#">Quên mật khẩu?</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const showPassword = ref(false);
const identifier = ref("");  // Chứa username, email hoặc phone_number
const password = ref("");

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

const login = async () => {
  try {
    const response = await axios.post('http://localhost:5000/api/accounts/login', {
      identifier: identifier.value,  // Dùng chung cho username, email hoặc số điện thoại
      password: password.value
    });
    alert('Đăng nhập thành công');
  } catch (error) {
    alert('Đăng nhập thất bại');
  }
};
</script>

<style scoped>
/* Container chính */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f8f9fa;
}

/* Hộp đăng nhập */
.login-box {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 400px;
}

/* Logo */
.logo {
  width: 80%;
  margin-bottom: 20px;
}

/* Ô nhập */
.input-field {
  width: 100%;
  padding: 10px;
  padding-right: 40px; /* Chừa chỗ cho icon */
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

/* Container của ô mật khẩu */
.password-container {
  position: relative;
  width: 100%;
}

/* Icon con mắt */
.toggle-password {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  cursor: pointer;
  color: #888;
  font-size: 18px;
}

.toggle-password:hover {
  color: #007bff;
}

/* Nút đăng nhập */
.login-button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  margin-bottom: 20px;
}

.login-button:hover {
  background-color: #0056b3;
}

/* Quên mật khẩu */
.forgot-password {
  text-align: right;
}

.forgot-password a {
  color: #007bff;
  text-decoration: none;
  font-size: 14px;
}

.forgot-password a:hover {
  text-decoration: underline;
}
</style>
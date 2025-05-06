<template>
    <div class="login-container">
      <div class="login-box">
        <img src="/Logo.png" alt="Logo" class="logo" />
  
        <input 
          v-model="identifier" 
          type="text" 
          placeholder="Tên đăng nhập, Email hoặc số điện thoại" 
          class="input-field"
          @keyup.enter="login"
        />
  
        <!-- Trường nhập mật khẩu -->
        <div class="password-container">
          <input 
            :type="showPassword ? 'text' : 'password'" 
            v-model="password" 
            placeholder="Mật khẩu" 
            class="input-field"
            @keyup.enter="login"
          />
          <i 
            v-if="password.length > 0" 
            :class="showPassword ? 'bi bi-eye' : 'bi bi-eye-slash'" 
            class="toggle-password" 
            @click="togglePassword"
          ></i>
        </div>
  
        <button @click="login" class="login-button">Đăng nhập</button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  
        <div class="forgot-password" @click="forgotPassword">
          <a href="#">Quên mật khẩu?</a>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import api from "@/utils/api";
  import { useRouter } from "vue-router";
  
  const showPassword = ref(false);
  const identifier = ref("");
  const password = ref("");
  const isActive = ref(true);
  const errorMessage = ref("");
  const router = useRouter();
  
  const togglePassword = () => {
    showPassword.value = !showPassword.value;
  };
  
  const login = async () => {
  errorMessage.value = "";
  
  if (!identifier.value || !password.value) {
    errorMessage.value = "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu";
    return;
  }

  try {
    const response = await api.post("/accounts/login", {
      identifier: identifier.value,
      password: password.value,
    });
    
    if (response.data.isActive === false) {
      errorMessage.value = "Tài khoản của bạn đã bị khóa!";
      return;
    }
    
    // Lưu thông tin người dùng và token
    localStorage.setItem("user_role", response.data.role);
    localStorage.setItem("username", response.data.username);
    localStorage.setItem("auth_token", response.data.token); // Lưu JWT token
    
    // Lưu student_id hoặc teacher_id nếu có
    if (response.data.student_id) {
      localStorage.setItem("student_id", response.data.student_id);
    }
    if (response.data.teacher_id) {
      localStorage.setItem("teacher_id", response.data.teacher_id);
    }
    
    router.push("/");
  } catch (error) {
      if (error.response) {
        switch (error.response.status) {
          case 404:
            errorMessage.value = "Tài khoản không tồn tại!";
            break;
          case 401:
            errorMessage.value = "Mật khẩu không chính xác!";
            break;
          default:
            errorMessage.value = "Đã xảy ra lỗi, vui lòng thử lại!";
        }
      } else {
        errorMessage.value = "Lỗi kết nối đến server";
      }
    }
  };
  
  const forgotPassword = () => {
    alert("Chức năng chưa cập nhật!");
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
  
  .input-field:focus {
    outline: none;
    border-color: #007bff;
  }
  
  /* Container của ô mật khẩu */
  .password-container {
    position: relative;
    width: 100%;
  }
  
  /* Icon con mắt */
  .toggle-password {
    position: absolute;
    top: 45%;
    right: 10px;
    transform: translateY(-50%);
    cursor: pointer;
    color: #888;
    font-size: 18px;
  }
  
  .toggle-password:hover {
    color: #007bff;
  }
  
  .login-button {
    width: 100%;
    padding: 10px;
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    margin-bottom: 20px;
    transition: 0.3s ease-in-out;
  }
  
  .login-button:hover {
    background: linear-gradient(135deg, #0056b3, #00408f);
  }
  
  .login-button:focus {
    outline: none;
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
  
  .error-message {
    color: red;
    font-size: 14px;
    margin-top: 5px;
  }
  </style>

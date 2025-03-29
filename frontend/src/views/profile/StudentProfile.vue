<template>
  <div class="container mt-4">
    <h2 class="mb-4">Thông tin cá nhân</h2>
    
    <!-- Hiển thị thông báo -->
    <div v-if="message" :class="'alert alert-' + messageType" role="alert">
      {{ message }}
    </div>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Đang tải thông tin...</p>
    </div>

    <div v-else-if="!student" class="alert alert-warning">
      Không thể tải thông tin sinh viên. Vui lòng thử lại sau.
    </div>
    
    <div v-else class="row">
      <!-- Thông tin cá nhân -->
      <div class="col-md-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Thông tin cá nhân</h5>
            <button class="btn btn-sm btn-primary" @click="isEditing = !isEditing">
              <i class="bi bi-pencil-square me-1"></i>{{ isEditing ? 'Hủy' : 'Chỉnh sửa' }}
            </button>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveProfile">
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Mã sinh viên</label>
                  <input type="text" class="form-control" :value="student.id" disabled>
                </div>
                <div class="col-md-6">
                  <label class="form-label">CMND/CCCD</label>
                  <input type="text" class="form-control" :value="student.identity_number" disabled>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Tên</label>
                  <input type="text" class="form-control" v-model="editedStudent.first_name" disabled>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Họ</label>
                  <input type="text" class="form-control" v-model="editedStudent.last_name" disabled>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Email</label>
                  <input type="email" class="form-control" v-model="editedStudent.email" 
                    :disabled="!isEditing"
                    maxlength="255">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Số điện thoại</label>
                  <input type="tel" class="form-control" v-model="editedStudent.phone_number" 
                    :disabled="!isEditing"
                    maxlength="10" 
                    pattern="[0-9]{10}" 
                    title="Số điện thoại phải có đúng 10 chữ số">
                  <div v-if="isEditing" class="form-text">Số điện thoại phải có đúng 10 chữ số</div>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Giới tính</label>
                  <select class="form-select" v-model="editedStudent.gender" disabled>
                    <option value="MALE">Nam</option>
                    <option value="FEMALE">Nữ</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Ngày sinh</label>
                  <input type="date" class="form-control" v-model="editedStudent.birthday" disabled>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Địa chỉ</label>
                <textarea class="form-control" v-model="editedStudent.address" rows="2" disabled></textarea>
              </div>
              
              <div v-if="isEditing" class="d-grid gap-2">
                <button type="submit" class="btn btn-success">
                  <i class="bi bi-check-circle me-1"></i>Lưu thay đổi
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- Ảnh đại diện và thông tin tài khoản -->
      <div class="col-md-4">
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Ảnh đại diện</h5>
          </div>
          <div class="card-body text-center">
            <img :src="student.avatar_url || placeholderImage" alt="Avatar" class="rounded-circle img-fluid" style="max-width: 150px;">
            <div v-if="isEditing" class="mt-3">
              <input type="file" ref="fileInput" @change="handleFileChange" accept="image/*" class="d-none" />
              <button type="button" class="btn btn-outline-primary btn-sm" @click="$refs.fileInput.click()">
                <i class="bi bi-upload me-1"></i>Tải ảnh lên
              </button>
              <p v-if="uploadStatus" class="small mt-2" :class="uploadStatus.type">{{ uploadStatus.message }}</p>
            </div>
          </div>
        </div>
        
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Thông tin tài khoản</h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input type="text" class="form-control" :value="username" disabled>
            </div>
            <div class="mb-3">
              <label class="form-label">Mật khẩu</label>
              <div class="input-group">
                <input type="password" class="form-control" value="********" disabled>
                <button class="btn btn-outline-secondary" type="button" @click="openChangePasswordModal" :disabled="!isEditing">
                  <i class="bi bi-key me-1"></i>Đổi
                </button>
              </div>
              <p v-if="!isEditing" class="text-muted small mt-2">Bấm "Chỉnh sửa" để đổi mật khẩu</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

// State
const student = ref(null);
const editedStudent = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  birthday: '',
  address: '',
  gender: 'MALE'
});
const loading = ref(true);
const isEditing = ref(false);
const message = ref('');
const messageType = ref('success');

const fileInput = ref(null);
const uploadStatus = ref(null);
const username = ref('');
const placeholderImage = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='150' height='150' viewBox='0 0 150 150'%3E%3Crect width='150' height='150' fill='%23EEEEEE'/%3E%3Ctext x='75' y='75' font-family='Arial' font-size='20' text-anchor='middle' dominant-baseline='middle' fill='%23AAAAAA'%3ENO IMAGE%3C/text%3E%3C/svg%3E";

// Life cycle
onMounted(async () => {
  // Get username from localStorage
  username.value = localStorage.getItem('username') || '';
  await fetchProfile();
});

// Methods
const fetchProfile = async () => {
  try {
    loading.value = true;
    const token = localStorage.getItem('auth_token');
    const response = await axios.get('http://localhost:5000/api/profile', {
      headers: {
        'Authorization': token
      }
    });
    
    student.value = response.data;
    
    // Copy data to editable object
    Object.assign(editedStudent, {
      first_name: student.value.first_name,
      last_name: student.value.last_name,
      email: student.value.email,
      phone_number: student.value.phone_number,
      birthday: student.value.birthday,
      address: student.value.address,
      gender: student.value.gender || 'MALE'
    });
  } catch (error) {
    showMessage('Không thể tải thông tin cá nhân: ' + (error.response?.data?.message || error.message), 'danger');
  } finally {
    loading.value = false;
  }
};

const saveProfile = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    // Chỉ gửi các trường được phép cập nhật
    const updateData = {
      email: editedStudent.email,
      phone_number: editedStudent.phone_number
    };
    
    await axios.put(`http://localhost:5000/api/students/${student.value.id}`, updateData, {
      headers: {
        'Authorization': token
      }
    });
    
    // Update local data
    student.value.email = editedStudent.email;
    student.value.phone_number = editedStudent.phone_number;
    
    // Exit edit mode
    isEditing.value = false;
    
    showMessage('Thông tin cá nhân đã được cập nhật thành công!', 'success');
  } catch (error) {
    showMessage('Không thể cập nhật thông tin: ' + (error.response?.data?.message || error.message), 'danger');
  }
};

const handleFileChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // Kiểm tra kích thước file (dưới 2MB)
  if (file.size > 2 * 1024 * 1024) {
    uploadStatus.value = {
      message: 'Ảnh phải có kích thước dưới 2MB',
      type: 'text-danger'
    };
    return;
  }
  
  // Kiểm tra định dạng file
  if (!file.type.match('image.*')) {
    uploadStatus.value = {
      message: 'Vui lòng chọn file ảnh hợp lệ',
      type: 'text-danger'
    };
    return;
  }
  
  uploadStatus.value = {
    message: 'Đang tải ảnh lên...',
    type: 'text-info'
  };
  
  try {
    // Chuyển file thành Base64
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = async () => {
      const base64Image = reader.result;
      
      // Gửi lên server
      const token = localStorage.getItem('auth_token');
      const response = await axios.post('http://localhost:5000/api/upload-avatar', {
        image: base64Image
      }, {
        headers: {
          'Authorization': token
        }
      });
      
      // Cập nhật avatar_url
      student.value.avatar_url = response.data.avatar_url;
      
      uploadStatus.value = {
        message: 'Tải ảnh lên thành công!',
        type: 'text-success'
      };
      
      // Xóa thông báo sau 3 giây
      setTimeout(() => {
        uploadStatus.value = null;
      }, 3000);
    };
  } catch (error) {
    uploadStatus.value = {
      message: 'Không thể tải ảnh lên: ' + (error.response?.data?.message || error.message),
      type: 'text-danger'
    };
  }
};

const openChangePasswordModal = () => {
  // TODO: Implement password change functionality
  showMessage('Chức năng đang được phát triển!', 'info');
};

const showMessage = (text, type = 'success') => {
  message.value = text;
  messageType.value = type;
  
  // Auto hide after 5 seconds
  setTimeout(() => {
    message.value = '';
  }, 5000);
};
</script> 
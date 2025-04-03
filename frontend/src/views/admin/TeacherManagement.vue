<template>
  <div class="container mt-4">
    <h2 class="mb-4">Quản lý giảng viên</h2>
    
    <!-- Hiển thị thông báo -->
    <div v-if="message" :class="'alert alert-' + messageType" role="alert">
      {{ message }}
    </div>
    
    <!-- Nút thêm mới -->
    <div class="mb-3">
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-plus-circle me-2"></i>Thêm giảng viên mới
      </button>
    </div>
    
    <!-- Bảng hiển thị danh sách giảng viên -->
    <div class="table-responsive">
      <table class="table table-striped table-hover">
        <thead>
          <tr>
            <th>ID</th>
            <th>CMND/CCCD</th>
            <th>Tên</th>
            <th>Họ</th>
            <th>Email</th>
            <th>Số điện thoại</th>
            <th>Giới tính</th>
            <th>Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="teacher in teachers" :key="teacher.id">
            <td>{{ teacher.id }}</td>
            <td>{{ teacher.identity_number }}</td>
            <td>{{ teacher.first_name }}</td>
            <td>{{ teacher.last_name }}</td>
            <td>{{ teacher.email }}</td>
            <td>{{ teacher.phone_number }}</td>
            <td>{{ teacher.gender == 'MALE' ? 'Nam' : 'Nữ' }}</td>
            <td>
              <button class="btn btn-sm btn-info me-2" @click="openEditModal(teacher)">
                <i class="bi bi-pencil-square"></i>
              </button>
              <button class="btn btn-sm btn-danger" @click="openDeleteModal(teacher)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Modal thêm/sửa giảng viên -->
    <div class="modal fade" id="teacherModal" tabindex="-1" aria-hidden="true" ref="teacherModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Cập nhật giảng viên' : 'Thêm giảng viên mới' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveTeacher">
              <div class="row">
                <div class="col-md-9">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">ID <span class="text-danger">*</span></label>
                      <input type="text" class="form-control" v-model="currentTeacher.id" 
                        :disabled="isEditing" 
                        maxlength="11" 
                        pattern="[A-Za-z0-9]{11}" 
                        title="ID phải có đúng 11 ký tự" 
                        required>
                      <div class="form-text">ID phải có đúng 11 ký tự</div>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">CCCD <span class="text-danger">*</span></label>
                      <input type="text" class="form-control" v-model="currentTeacher.identity_number" 
                        maxlength="12" 
                        pattern="[0-9]{12}" 
                        title="CCCD phải có đúng 12 chữ số" 
                        required>
                      <div class="form-text">CCCD phải có đúng 12 chữ số</div>
                    </div>
                  </div>
                  
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Tên <span class="text-danger">*</span></label>
                      <input type="text" class="form-control" v-model="currentTeacher.first_name" required>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Họ <span class="text-danger">*</span></label>
                      <input type="text" class="form-control" v-model="currentTeacher.last_name" required>
                    </div>
                  </div>
                  
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Email</label>
                      <input type="email" class="form-control" v-model="currentTeacher.email" maxlength="255">
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Số điện thoại</label>
                      <input type="tel" class="form-control" v-model="currentTeacher.phone_number" 
                        maxlength="10" 
                        pattern="[0-9]{10}" 
                        title="Số điện thoại phải có đúng 10 chữ số">
                      <div class="form-text">Số điện thoại phải có đúng 10 chữ số</div>
                    </div>
                  </div>
                  
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Giới tính <span class="text-danger">*</span></label>
                      <select class="form-select" v-model="currentTeacher.gender" required>
                        <option value="MALE">Nam</option>
                        <option value="FEMALE">Nữ</option>
                      </select>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Ngày sinh <span class="text-danger">*</span></label>
                      <input type="date" class="form-control" v-model="currentTeacher.birthday" required>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">Địa chỉ <span class="text-danger">*</span></label>
                    <textarea class="form-control" v-model="currentTeacher.address" rows="2" required></textarea>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">Tiểu sử</label>
                    <textarea class="form-control" v-model="currentTeacher.bio" rows="3"></textarea>
                  </div>
                </div>
                
                <!-- Thêm phần upload avatar -->
                <div class="col-md-3">
                  <div class="mb-3 text-center">
                    <label class="form-label">Ảnh đại diện</label>
                    <div class="d-flex flex-column align-items-center">
                      <img :src="currentTeacher.avatar_url || placeholderImage" alt="Avatar" class="rounded-circle img-fluid mb-2" style="width: 150px; height: 150px; object-fit: cover;">
                      <input type="file" ref="avatarInput" @change="handleFileChange" accept="image/*" class="d-none">
                      <button type="button" class="btn btn-sm btn-outline-primary" @click="$refs.avatarInput.click()">
                        <i class="bi bi-upload me-1"></i>Chọn ảnh
                      </button>
                      <p v-if="uploadStatus" class="small mt-2" :class="uploadStatus.type">{{ uploadStatus.message }}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Tài khoản (chỉ hiển thị khi thêm mới) -->
              <div v-if="!isEditing">
                <hr>
                <h5>Tạo tài khoản</h5>
                
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Tên đăng nhập <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" v-model="accountData.username" required>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Mật khẩu <span class="text-danger">*</span></label>
                    <input type="password" class="form-control" v-model="accountData.password" required>
                  </div>
                </div>
              </div>
              
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
                <button type="submit" class="btn btn-primary">Lưu</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal xóa giảng viên -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Bạn có chắc chắn muốn xóa giảng viên <strong>{{ deleteTeacherName }}</strong>?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteTeacher">Xóa</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { Modal } from 'bootstrap';

// State
const teachers = ref([]);
const currentTeacher = ref({
  id: '',
  identity_number: '',
  email: '',
  phone_number: '',
  first_name: '',
  last_name: '',
  birthday: '',
  address: '',
  gender: 'MALE',
  bio: ''
});
const accountData = ref({
  username: '',
  password: '',
});
const isEditing = ref(false);
const message = ref('');
const messageType = ref('success');
const teacherModal = ref(null);
const deleteModal = ref(null);
const deleteTeacherId = ref(null);
const deleteTeacherName = ref('');
const uploadStatus = ref(null);
const avatarInput = ref(null);
const placeholderImage = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='150' height='150' viewBox='0 0 150 150'%3E%3Crect width='150' height='150' fill='%23EEEEEE'/%3E%3Ctext x='75' y='75' font-family='Arial' font-size='20' text-anchor='middle' dominant-baseline='middle' fill='%23AAAAAA'%3ENO IMAGE%3C/text%3E%3C/svg%3E";

// Life cycle
onMounted(async () => {
  await fetchTeachers();
});

// Methods
const fetchTeachers = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await axios.get('http://localhost:5000/api/teachers', {
      headers: {
        'Authorization': token
      }
    });
    teachers.value = response.data;
  } catch (error) {
    showMessage('Không thể tải danh sách giảng viên', 'danger');
  }
};

const openAddModal = () => {
  isEditing.value = false;
  // Reset form
  currentTeacher.value = {
    id: '',
    identity_number: '',
    email: '',
    phone_number: '',
    first_name: '',
    last_name: '',
    birthday: '',
    address: '',
    gender: 'MALE',
    bio: ''
  };
  accountData.value = {
    username: '',
    password: ''
  };
  
  // Show modal
  new Modal(teacherModal.value).show();
};

const openEditModal = (teacher) => {
  isEditing.value = true;
  currentTeacher.value = { ...teacher };
  
  // Show modal
  new Modal(teacherModal.value).show();
};

const openDeleteModal = (teacher) => {
  deleteTeacherId.value = teacher.id;
  deleteTeacherName.value = `${teacher.first_name} ${teacher.last_name}`;
  
  // Show modal
  new Modal(deleteModal.value).show();
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
      
      // Tạm lưu ảnh vào biến currentTeacher để hiển thị preview
      // Không gửi trực tiếp lên server, mà sẽ gửi cùng khi tạo/cập nhật giảng viên
      currentTeacher.value.avatar_data = base64Image;
      currentTeacher.value.avatar_url = base64Image; // Để hiển thị preview
      
      uploadStatus.value = {
        message: 'Ảnh đã sẵn sàng để tải lên',
        type: 'text-success'
      };
      
      // Xóa thông báo sau 3 giây
      setTimeout(() => {
        uploadStatus.value = null;
      }, 3000);
    };
  } catch (error) {
    uploadStatus.value = {
      message: 'Lỗi xử lý ảnh: ' + error.message,
      type: 'text-danger'
    };
  }
};

const saveTeacher = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    
    if (isEditing.value) {
      // Update existing teacher
      const teacherData = { ...currentTeacher.value };
      
      // Xử lý avatar nếu có
      if (teacherData.avatar_data) {
        // Upload avatar trước
        const avatarResponse = await axios.post('http://localhost:5000/api/upload-avatar', {
          image: teacherData.avatar_data,
          teacher_id: teacherData.id  // Thêm teacher_id để API biết cập nhật cho ai
        }, {
          headers: { 'Authorization': token }
        });
        
        // Cập nhật avatar_url và xóa avatar_data
        teacherData.avatar_url = avatarResponse.data.avatar_url;
        delete teacherData.avatar_data;
      }
      
      await axios.put(`http://localhost:5000/api/teachers/${teacherData.id}`, teacherData, {
        headers: { 'Authorization': token }
      });
      
      showMessage('Giảng viên đã được cập nhật thành công!', 'success');
    } else {
      // Create new teacher
      const teacherData = { ...currentTeacher.value };
      
      // Xử lý avatar nếu có
      let avatarUrl = null;
      if (teacherData.avatar_data) {
        delete teacherData.avatar_url; // Xóa URL tạm thời
        
        // Lưu lại dữ liệu avatar để dùng sau
        const avatarData = teacherData.avatar_data;
        delete teacherData.avatar_data; // Xóa dữ liệu ảnh tạm thời
      }
      
      // Tạo giảng viên
      await axios.post('http://localhost:5000/api/teachers', teacherData, {
        headers: { 'Authorization': token }
      });
      
      // Create account for new teacher
      if (accountData.value.username && accountData.value.password) {
        await axios.post('http://localhost:5000/api/accounts', {
          username: accountData.value.username,
          password: accountData.value.password,
          email: currentTeacher.value.email,
          phone_number: currentTeacher.value.phone_number,
          role: 'teacher',
          teacher_id: currentTeacher.value.id,
          is_active: true
        }, {
          headers: { 'Authorization': token }
        });
        
        // Upload avatar nếu có
        if (avatarData) {
          await axios.post('http://localhost:5000/api/upload-avatar', {
            image: avatarData,
            teacher_id: currentTeacher.value.id  // Thêm teacher_id để API biết cập nhật cho ai
          }, {
            headers: { 'Authorization': token }
          });
        }
      }
      
      showMessage('Giảng viên mới đã được tạo thành công!', 'success');
    }
    
    // Close modal & refresh list
    Modal.getInstance(teacherModal.value).hide();
    await fetchTeachers();
  } catch (error) {
    showMessage('Đã xảy ra lỗi: ' + (error.response?.data?.message || error.message), 'danger');
  }
};

const deleteTeacher = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    await axios.delete(`http://localhost:5000/api/teachers/${deleteTeacherId.value}`, {
      headers: {
        'Authorization': token
      }
    });
    
    showMessage('Giảng viên đã được xóa thành công!', 'success');
    
    // Close modal & refresh list
    Modal.getInstance(deleteModal.value).hide();
    await fetchTeachers();
  } catch (error) {
    showMessage('Đã xảy ra lỗi: ' + (error.response?.data?.message || error.message), 'danger');
  }
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
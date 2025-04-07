<template>
  <div class="subject-management">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Quản Lý Môn Học</h4>
        <button @click="openCreateModal" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i>Thêm Môn Học Mới
        </button>
      </div>
      
      <div class="card-body">
        <!-- Search and filter -->
        <div class="row mb-3">
          <div class="col-md-6">
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input 
                type="text" 
                class="form-control" 
                placeholder="Tìm kiếm theo mã hoặc tên môn học..." 
                v-model="searchQuery"
                @input="handleSearchInput"
              >
              <button class="btn btn-outline-secondary" type="button" @click="fetchSubjects">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" v-model="sortBy" @change="sortSubjects">
              <option value="code">Sắp xếp theo mã</option>
              <option value="name">Sắp xếp theo tên</option>
              <option value="credit">Sắp xếp theo số tín chỉ</option>
            </select>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" v-model="sortOrder" @change="sortSubjects">
              <option value="asc">Tăng dần</option>
              <option value="desc">Giảm dần</option>
            </select>
          </div>
        </div>
        
        <!-- Loading spinner -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Đang tải dữ liệu...</p>
        </div>
        
        <!-- Subjects table -->
        <div v-else-if="subjects.length" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Mã môn học</th>
                <th scope="col">Tên môn học</th>
                <th scope="col">Số tín chỉ</th>
                <th scope="col">Mô tả</th>
                <th scope="col">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(subject, index) in subjects" :key="subject.id">
                <td>{{ index + 1 }}</td>
                <td>{{ subject.code }}</td>
                <td>{{ subject.name }}</td>
                <td>{{ subject.credit }}</td>
                <td>
                  <span v-if="subject.description" class="d-inline-block text-truncate" style="max-width: 250px;">
                    {{ subject.description }}
                  </span>
                  <span v-else class="text-muted">Không có mô tả</span>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button @click="openEditModal(subject)" class="btn btn-outline-primary">
                      <i class="bi bi-pencil-square"></i>
                    </button>
                    <button @click="confirmDelete(subject)" class="btn btn-outline-danger">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- No subjects found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Không tìm thấy môn học nào.</p>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Modal -->
    <div class="modal fade" id="subjectModal" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Cập nhật môn học' : 'Thêm môn học mới' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="isEditing ? updateSubject() : createSubject()">
              <div class="mb-3">
                <label class="form-label">Mã môn học <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentSubject.code" required maxlength="10">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Tên môn học <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentSubject.name" required>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Số tín chỉ <span class="text-danger">*</span></label>
                <input type="number" class="form-control" v-model="currentSubject.credit" required min="1" max="10">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Mô tả</label>
                <textarea class="form-control" v-model="currentSubject.description" rows="3"></textarea>
              </div>
              
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Hủy</button>
                <button type="submit" class="btn btn-primary" :disabled="processing">
                  <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
                  {{ isEditing ? 'Cập nhật' : 'Thêm mới' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa môn học <strong>{{ deleteSubjectName }}</strong> ({{ deleteSubjectCode }}) không?</p>
            <p class="text-danger"><small>Hành động này không thể hoàn tác.</small></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteSubject" :disabled="processing">
              <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
              Xóa
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast Notification -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div id="notification" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header" :class="{'bg-success text-white': toastType === 'success', 'bg-danger text-white': toastType === 'error'}">
          <strong class="me-auto">{{ toastTitle }}</strong>
          <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
          {{ toastMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';
import { Modal, Toast } from 'bootstrap';

export default {
  name: 'SubjectManagement',
  setup() {
    // State
    const subjects = ref([]);
    const searchQuery = ref('');
    const loading = ref(true);
    const processing = ref(false);
    const isEditing = ref(false);
    const deleteSubjectId = ref(null);
    const deleteSubjectName = ref('');
    const deleteSubjectCode = ref('');
    const sortBy = ref('code');
    const sortOrder = ref('asc');
    const toastTitle = ref('Thông báo');
    const toastMessage = ref('');
    const toastType = ref('success');

    // Bootstrap modal instances
    let subjectModal = null;
    let deleteModal = null;
    let toastNotification = null;

    // Current subject being edited/created
    const currentSubject = reactive({
      id: null,
      code: '',
      name: '',
      credit: 3,
      description: ''
    });
    
    // Initialize UI components after mount
    onMounted(() => {
      fetchSubjects();
      
      subjectModal = new Modal(document.getElementById('subjectModal'));
      deleteModal = new Modal(document.getElementById('deleteModal'));
      toastNotification = new Toast(document.getElementById('notification'));
    });
    
    // Methods
    const fetchSubjects = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get('http://localhost:5000/api/subjects', {
          headers: {
            'Authorization': token
          }
        });
        subjects.value = response.data;
        sortSubjects(); // Apply default sorting
      } catch (error) {
        console.error('Error fetching subjects:', error);
        showNotification('Lỗi', 'Không thể tải danh sách môn học', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const sortSubjects = () => {
      subjects.value.sort((a, b) => {
        let valueA = a[sortBy.value];
        let valueB = b[sortBy.value];
        
        if (typeof valueA === 'string') {
          valueA = valueA.toLowerCase();
          valueB = valueB.toLowerCase();
        }
        
        if (sortOrder.value === 'asc') {
          return valueA > valueB ? 1 : -1;
        } else {
          return valueA < valueB ? 1 : -1;
        }
      });
    };
    
    const handleSearchInput = () => {
      // Implement debounce logic here if needed
      fetchSubjects();
    };
    
    const resetForm = () => {
      currentSubject.id = null;
      currentSubject.code = '';
      currentSubject.name = '';
      currentSubject.credit = 3;
      currentSubject.description = '';
    };
    
    const openCreateModal = () => {
      resetForm();
      isEditing.value = false;
      subjectModal.show();
    };
    
    const openEditModal = (subject) => {
      currentSubject.id = subject.id;
      currentSubject.code = subject.code;
      currentSubject.name = subject.name;
      currentSubject.credit = subject.credit;
      currentSubject.description = subject.description || '';
      
      isEditing.value = true;
      subjectModal.show();
    };
    
    const createSubject = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.post('http://localhost:5000/api/subjects', currentSubject, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchSubjects();
        subjectModal.hide();
        showNotification('Thành công', 'Thêm môn học mới thành công', 'success');
      } catch (error) {
        console.error('Error creating subject:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể thêm môn học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const updateSubject = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.put(`http://localhost:5000/api/subjects/${currentSubject.id}`, currentSubject, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchSubjects();
        subjectModal.hide();
        showNotification('Thành công', 'Cập nhật môn học thành công', 'success');
      } catch (error) {
        console.error('Error updating subject:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể cập nhật môn học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const confirmDelete = (subject) => {
      deleteSubjectId.value = subject.id;
      deleteSubjectName.value = subject.name;
      deleteSubjectCode.value = subject.code;
      deleteModal.show();
    };
    
    const deleteSubject = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.delete(`http://localhost:5000/api/subjects/${deleteSubjectId.value}`, {
          headers: {
            'Authorization': token
          }
        });
        
        await fetchSubjects();
        deleteModal.hide();
        showNotification('Thành công', 'Xóa môn học thành công', 'success');
      } catch (error) {
        console.error('Error deleting subject:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể xóa môn học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const showNotification = (title, message, type) => {
      toastTitle.value = title;
      toastMessage.value = message;
      toastType.value = type;
      toastNotification.show();
    };
    
    return {
      subjects,
      searchQuery,
      loading,
      processing,
      isEditing,
      currentSubject,
      deleteSubjectId,
      deleteSubjectName,
      deleteSubjectCode,
      sortBy,
      sortOrder,
      toastTitle,
      toastMessage,
      toastType,
      fetchSubjects,
      handleSearchInput,
      sortSubjects,
      openCreateModal,
      openEditModal,
      createSubject,
      updateSubject,
      confirmDelete,
      deleteSubject
    };
  }
};
</script>

<style scoped>
.subject-management {
  padding: 20px;
}
</style>

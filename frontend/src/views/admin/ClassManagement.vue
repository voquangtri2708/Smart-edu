<template>
  <div class="class-management">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Quản Lý Lớp Học</h4>
        <button @click="openCreateModal" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i>Thêm Lớp Học Mới
        </button>
      </div>
      
      <div class="card-body">
        <!-- Hiển thị thông báo -->
        <div v-if="message" :class="'alert alert-' + messageType" role="alert">
          {{ message }}
        </div>
        
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
                placeholder="Tìm kiếm theo mã lớp học..." 
                v-model="searchQuery"
                @input="handleSearchInput"
              >
              <button class="btn btn-outline-secondary" type="button" @click="fetchClasses">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" v-model="sortBy" @change="sortClasses">
              <option value="code">Sắp xếp theo mã lớp</option>
              <option value="start_date">Sắp xếp theo ngày bắt đầu</option>
              <option value="end_date">Sắp xếp theo ngày kết thúc</option>
            </select>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" v-model="sortOrder" @change="sortClasses">
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
        
        <!-- Classes table -->
        <div v-else-if="classes.length" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Mã lớp</th>
                <th scope="col">Môn học</th>
                <th scope="col">Sĩ số tối đa</th>
                <th scope="col">Ngày bắt đầu</th>
                <th scope="col">Ngày kết thúc</th>
                <th scope="col">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(classItem, index) in classes" :key="classItem.id">
                <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                <td>{{ classItem.code }}</td>
                <td>{{ getSubjectName(classItem.subject_id) }}</td>
                <td>{{ classItem.max_student }}</td>
                <td>{{ formatDate(classItem.start_date) }}</td>
                <td>{{ formatDate(classItem.end_date) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button @click="openEditModal(classItem)" class="btn btn-outline-primary" title="Sửa">
                      <i class="bi bi-pencil-square"></i>
                    </button>
                    <button @click="confirmDelete(classItem)" class="btn btn-outline-danger" title="Xóa">
                      <i class="bi bi-trash"></i>
                    </button>
                    <router-link :to="`/admin/class-students/${classItem.id}`" class="btn btn-outline-success" title="Quản lý sinh viên">
                      <i class="bi bi-people-fill"></i>
                    </router-link>
                    <router-link :to="`/admin/class-teachers/${classItem.id}`" class="btn btn-outline-info" title="Quản lý giáo viên">
                      <i class="bi bi-person-workspace"></i>
                    </router-link>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Pagination -->
          <Pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :total-items="totalItems"
            :total-pages="totalPages"
            item-label="lớp học"
            @page-change="changePage"
            @page-size-change="changePageSize"
          />
        </div>
        
        <!-- No classes found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Không tìm thấy lớp học nào.</p>
        </div>
      </div>
    </div>
    
    <!-- Modal thêm/sửa lớp học -->
    <div class="modal fade" id="classModal" tabindex="-1" data-bs-backdrop="static" ref="classModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Cập nhật lớp học' : 'Thêm lớp học mới' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="isEditing ? updateClass() : createClass()">
              <div class="mb-3">
                <label class="form-label">Mã lớp học <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentClass.code" required maxlength="50">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Môn học <span class="text-danger">*</span></label>
                <select class="form-select" v-model="currentClass.subject_id" required>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.code }} - {{ subject.name }}
                  </option>
                </select>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Sĩ số tối đa <span class="text-danger">*</span></label>
                <input type="number" class="form-control" v-model="currentClass.max_student" required min="1" max="100">
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Ngày bắt đầu <span class="text-danger">*</span></label>
                  <VueFlatpickr
                    v-model="currentClass.start_date"
                    class="form-control"
                    placeholder="DD/MM/YYYY"
                    :config="flatpickrConfig"
                    required
                  />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Ngày kết thúc <span class="text-danger">*</span></label>
                  <VueFlatpickr
                    v-model="currentClass.end_date"
                    class="form-control"
                    placeholder="DD/MM/YYYY"
                    :config="flatpickrConfig"
                    required
                  />
                </div>
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
    <div class="modal fade" id="deleteModal" tabindex="-1" data-bs-backdrop="static" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa lớp học <strong>{{ deleteClassName }}</strong> không?</p>
            <p class="text-danger"><small>Hành động này không thể hoàn tác.</small></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteClass" :disabled="processing">
              <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
              Xóa
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast Notification -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div id="notification" class="toast" role="alert" aria-live="assertive" aria-atomic="true" ref="toastNotification">
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
import VueFlatpickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';
import Vietnamese from 'flatpickr/dist/l10n/vn.js';
import Pagination from '@/components/Pagination.vue';

export default {
  name: 'ClassManagement',
  components: {
    VueFlatpickr,
    Pagination
  },
  setup() {
    // State
    const classes = ref([]);
    const subjects = ref([]);
    const searchQuery = ref('');
    const loading = ref(true);
    const processing = ref(false);
    const isEditing = ref(false);
    const message = ref('');
    const messageType = ref('info');
    const sortBy = ref('code');
    const sortOrder = ref('asc');
    
    // Pagination state
    const currentPage = ref(1);
    const pageSize = ref(10);
    const totalItems = ref(0);
    const totalPages = ref(0);
    
    // Flatpickr configuration
    const flatpickrConfig = {
      dateFormat: 'Y-m-d',
      locale: Vietnamese.vn,
      allowInput: true,
      altFormat: 'd/m/Y',
      altInput: true
    };
    
    // Current class being edited
    const currentClass = reactive({
      id: null,
      code: '',
      subject_id: null,
      max_student: 30,
      start_date: '',
      end_date: ''
    });
    
    // Delete confirmation
    const deleteClassId = ref(null);
    const deleteClassName = ref('');
    
    // Toast notification
    const toastTitle = ref('');
    const toastMessage = ref('');
    const toastType = ref('success');
    
    // Mounted lifecycle hook
    onMounted(() => {
      // Fetch data
      fetchClasses();
      fetchSubjects();
    });
    
    // Methods
    const fetchClasses = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get('http://localhost:5000/api/classes', {
          params: {
            page: currentPage.value,
            per_page: pageSize.value,
            query: searchQuery.value || undefined
          },
          headers: {
            'Authorization': token
          }
        });
        
        // Update with paginated data
        if (response.data && response.data.items) {
          classes.value = response.data.items;
          
          // Update pagination info
          totalItems.value = response.data.pagination.total;
          totalPages.value = response.data.pagination.pages;
        } else {
          classes.value = response.data;
        }
        
        sortClasses(); // Apply default sorting
      } catch (error) {
        console.error('Error fetching classes:', error);
        showNotification('Lỗi', 'Không thể tải danh sách lớp học', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const fetchSubjects = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get('http://localhost:5000/api/subjects', {
          headers: {
            'Authorization': token
          }
        });
        
        // Check if response has pagination structure
        if (response.data && response.data.items) {
          // API returns paginated data
          subjects.value = response.data.items;
        } else {
          // API returns direct array
          subjects.value = response.data;
        }
        
        console.log("Loaded subjects:", subjects.value);
      } catch (error) {
        console.error('Error fetching subjects:', error);
        showNotification('Lỗi', 'Không thể tải danh sách môn học', 'error');
      }
    };
    
    const sortClasses = () => {
      classes.value.sort((a, b) => {
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
      // Reset to first page when searching
      currentPage.value = 1;
      fetchClasses();
    };
    
    const changePage = (page) => {
      currentPage.value = page;
      fetchClasses();
    };
    
    const changePageSize = (size) => {
      pageSize.value = size;
      currentPage.value = 1; // Reset to first page
      fetchClasses();
    };
    
    const resetForm = () => {
      currentClass.id = null;
      currentClass.code = '';
      currentClass.subject_id = subjects.value.length > 0 ? subjects.value[0].id : null;
      currentClass.max_student = 30;
      currentClass.start_date = '';
      currentClass.end_date = '';
    };
    
    const openCreateModal = () => {
      resetForm();
      isEditing.value = false;
      
      const modalElement = document.getElementById('classModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const openEditModal = (classItem) => {
      currentClass.id = classItem.id;
      currentClass.code = classItem.code;
      currentClass.subject_id = classItem.subject_id;
      currentClass.max_student = classItem.max_student;
      
      // Fix date formatting issues
      if (classItem.start_date) {
        // Use simple string split to get the date part
        currentClass.start_date = classItem.start_date.split('T')[0];
      } else {
        currentClass.start_date = '';
      }
      
      if (classItem.end_date) {
        // Use simple string split to get the date part
        currentClass.end_date = classItem.end_date.split('T')[0];
      } else {
        currentClass.end_date = '';
      }
      
      isEditing.value = true;
      
      const modalElement = document.getElementById('classModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const createClass = async () => {
      // Validate dates before submitting
      if (new Date(currentClass.end_date) <= new Date(currentClass.start_date)) {
        showNotification('Lỗi', 'Ngày kết thúc phải sau ngày bắt đầu', 'error');
        return;
      }
      
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.post('http://localhost:5000/api/classes', currentClass, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchClasses();
        
        const modalElement = document.getElementById('classModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Thêm lớp học mới thành công', 'success');
      } catch (error) {
        console.error('Error creating class:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể thêm lớp học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const updateClass = async () => {
      // Validate dates before submitting
      if (new Date(currentClass.end_date) <= new Date(currentClass.start_date)) {
        showNotification('Lỗi', 'Ngày kết thúc phải sau ngày bắt đầu', 'error');
        return;
      }
      
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.put(`http://localhost:5000/api/classes/${currentClass.id}`, currentClass, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchClasses();
        
        const modalElement = document.getElementById('classModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Cập nhật lớp học thành công', 'success');
      } catch (error) {
        console.error('Error updating class:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể cập nhật lớp học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const confirmDelete = (classItem) => {
      deleteClassId.value = classItem.id;
      deleteClassName.value = classItem.code;
      
      const modalElement = document.getElementById('deleteModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const deleteClass = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.delete(`http://localhost:5000/api/classes/${deleteClassId.value}`, {
          headers: {
            'Authorization': token
          }
        });
        
        await fetchClasses();
        
        const modalElement = document.getElementById('deleteModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Xóa lớp học thành công', 'success');
      } catch (error) {
        console.error('Error deleting class:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể xóa lớp học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const showNotification = (title, message, type) => {
      toastTitle.value = title;
      toastMessage.value = message;
      toastType.value = type;
      
      // Get the toast element and create instance if needed
      const toastElement = document.getElementById('notification');
      let toastInstance = Toast.getInstance(toastElement);
      
      if (!toastInstance) {
        toastInstance = new Toast(toastElement);
      }
      
      toastInstance.show();
    };
    
    const getSubjectName = (subjectId) => {
      const subject = subjects.value.find(s => s.id === subjectId);
      return subject ? `${subject.code} - ${subject.name}` : 'N/A';
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString('vi-VN', {
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric'
      });
    };
    
    return {
      classes,
      subjects,
      searchQuery,
      loading,
      processing,
      isEditing,
      message,
      messageType,
      currentClass,
      deleteClassId,
      deleteClassName,
      sortBy,
      sortOrder,
      toastTitle,
      toastMessage,
      toastType,
      flatpickrConfig,
      // Pagination
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      changePage,
      changePageSize,
      fetchClasses,
      fetchSubjects,
      handleSearchInput,
      sortClasses,
      openCreateModal,
      openEditModal,
      createClass,
      updateClass,
      confirmDelete,
      deleteClass,
      getSubjectName,
      formatDate
    };
  }
};
</script>

<style scoped>
.class-management {
  padding: 20px;
}
</style>
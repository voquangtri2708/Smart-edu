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
                @input="onSearchInput"
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
                <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
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
                    <button @click="openCreateClassModal(subject)" class="btn btn-outline-success">
                      <i class="bi bi-plus-square"></i>
                    </button>
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
            item-label="môn học"
            @page-change="changePage"
            @page-size-change="changePageSize"
          />
        </div>
        
        <!-- No subjects found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Không tìm thấy môn học nào.</p>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Modal -->
    <div class="modal fade" id="subjectModal" tabindex="-1" data-bs-backdrop="static" ref="subjectModal">
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
    <div class="modal fade" id="deleteModal" tabindex="-1" data-bs-backdrop="static" ref="deleteModal">
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
    
    <!-- Create Class Modal -->
    <div class="modal fade" id="createClassModal" tabindex="-1" data-bs-backdrop="static" ref="createClassModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Tạo lớp học mới cho môn {{ selectedSubject.name }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createClass()">
              <div class="mb-3">
                <label class="form-label">Mã lớp học <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="newClass.code" required maxlength="50">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Sĩ số tối đa <span class="text-danger">*</span></label>
                <input type="number" class="form-control" v-model="newClass.max_student" required min="1" max="100">
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Ngày bắt đầu <span class="text-danger">*</span></label>
                  <VueFlatpickr
                    v-model="newClass.start_date"
                    class="form-control"
                    placeholder="DD/MM/YYYY"
                    :config="flatpickrConfig"
                    required
                  />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Ngày kết thúc <span class="text-danger">*</span></label>
                  <VueFlatpickr
                    v-model="newClass.end_date"
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
                  Tạo lớp học
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast Notification -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div id="notification" class="toast" role="alert" aria-live="assertive" aria-atomic="true" ref="toastEl">
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
import { ref, reactive, onMounted, watch } from 'vue';
import api from '@/utils/api';
import { Modal, Toast } from 'bootstrap';
import Pagination from '@/components/Pagination.vue';
import { debounce } from '@/utils/debounce';
import VueFlatpickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';
import Vietnamese from 'flatpickr/dist/l10n/vn.js';

export default {
  name: 'SubjectManagement',
  components: {
    Pagination,
    VueFlatpickr
  },
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
    
    // Class creation state
    const selectedSubject = ref({});
    const newClass = reactive({
      code: '',
      subject_id: null,
      max_student: 30,
      start_date: '',
      end_date: ''
    });
    
    // Pagination state
    const currentPage = ref(1);
    const pageSize = ref(10);
    const totalItems = ref(0);
    const totalPages = ref(0);

    // Current subject being edited/created
    const currentSubject = reactive({
      id: null,
      code: '',
      name: '',
      credit: 3,
      description: ''
    });
    
    // Flatpickr configuration
    const flatpickrConfig = {
      dateFormat: 'Y-m-d',
      locale: Vietnamese.vn,
      allowInput: true,
      altFormat: 'd/m/Y',
      altInput: true,
      parseDate: (datestr, format) => {
        // Xử lý khi người dùng nhập 8 số liên tiếp
        if (/^\d{8}$/.test(datestr)) {
          return new Date(
            datestr.substr(4, 4) + '-' + 
            datestr.substr(2, 2) + '-' + 
            datestr.substr(0, 2)
          );
        }
        return null; // Let flatpickr handle other formats
      }
    };
    
    // Initialize UI components after mount
    onMounted(() => {
      fetchSubjects();
    });
    
    // Methods
    const fetchSubjects = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        const response = await api.get('/subjects', {
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
        subjects.value = response.data.items;
        
        // Update pagination info
        totalItems.value = response.data.pagination.total;
        totalPages.value = response.data.pagination.pages;
        
        sortSubjects(); // Apply default sorting
      } catch (error) {
        console.error('Error fetching subjects:', error);
        showNotification('Lỗi', 'Không thể tải danh sách môn học', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const sortSubjects = () => {
      // Note: This client-side sorting only sorts the current page
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
          return valueA < valueB ? -1 : 1;
        }
      });
    };
    
    const onSearchInput = () => {
      debouncedSearch();
    };

    const debouncedSearch = debounce(() => {
      currentPage.value = 1;
      fetchSubjects();
    }, 500);
    
    const changePage = (page) => {
      currentPage.value = page;
      fetchSubjects();
    };
    
    const changePageSize = (size) => {
      pageSize.value = size;
      currentPage.value = 1; // Reset to first page
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
      
      const modalElement = document.getElementById('subjectModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const openEditModal = (subject) => {
      currentSubject.id = subject.id;
      currentSubject.code = subject.code;
      currentSubject.name = subject.name;
      currentSubject.credit = subject.credit;
      currentSubject.description = subject.description || '';
      
      isEditing.value = true;
      
      const modalElement = document.getElementById('subjectModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const createSubject = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.post('/subjects', currentSubject, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
          
        await fetchSubjects();
          
        const modalElement = document.getElementById('subjectModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
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
        await api.put(`/subjects/${currentSubject.id}`, currentSubject, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchSubjects();
          
        const modalElement = document.getElementById('subjectModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
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
      
      const modalElement = document.getElementById('deleteModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const deleteSubject = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.delete(`/subjects/${deleteSubjectId.value}`, {
          headers: {
            'Authorization': token
          }
        });
         
        await fetchSubjects();
        
        const modalElement = document.getElementById('deleteModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
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
      
      const toastElement = document.getElementById('notification');
      let toastInstance = Toast.getInstance(toastElement);
      
      if (!toastInstance) {
        toastInstance = new Toast(toastElement);
      }
      
      toastInstance.show();
    };
    
    // Open the create class modal
    const openCreateClassModal = (subject) => {
      selectedSubject.value = subject;
      
      // Reset form and set subject ID
      newClass.code = `${subject.code}`;
      newClass.subject_id = subject.id;
      newClass.max_student = 30;
      
      // Set default dates (today and today + 3 months)
      const today = new Date();
      const endDate = new Date();
      endDate.setMonth(today.getMonth() + 3);
        
      newClass.start_date = today.toISOString().split('T')[0];
      newClass.end_date = endDate.toISOString().split('T')[0];
      
      // Display the modal - fixed to use the same pattern as other modals
      const modalElement = document.getElementById('createClassModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    // Create a new class
    const createClass = async () => {
      // Validate dates before submitting
      if (new Date(newClass.end_date) <= new Date(newClass.start_date)) {
        showNotification('Lỗi', 'Ngày kết thúc phải sau ngày bắt đầu', 'error');
        return;
      }
      
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.post('/classes', newClass, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        // Fixed to use Modal.getInstance for closing
        const modalElement = document.getElementById('createClassModal');
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
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      toastTitle,
      toastMessage,
      toastType,
      fetchSubjects,
      onSearchInput,
      openCreateModal,
      openEditModal,
      createSubject,
      updateSubject,
      confirmDelete,
      deleteSubject,
      sortSubjects,
      changePage,
      changePageSize,
      // Class creation
      selectedSubject,
      newClass,
      flatpickrConfig,
      openCreateClassModal,
      createClass
    };
  }
};
</script>

<style scoped>
.subject-management {
  padding: 20px;
}
</style>

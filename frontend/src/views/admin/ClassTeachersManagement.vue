<template>
  <div class="class-teachers-management">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <div>
          <h4 class="mb-0">Quản Lý Giáo Viên Lớp {{ classInfo.code }}</h4>
          <p class="mb-0 text-muted small">Môn học: {{ classInfo.subject_name || 'Đang tải...' }}</p>
        </div>
        <div>
          <button @click="openAddTeacherModal" class="btn btn-primary">
            <i class="bi bi-plus-circle me-1"></i>Thêm Giáo Viên
          </button>
          <router-link to="/admin/classes" class="btn btn-outline-secondary ms-2">
            <i class="bi bi-arrow-left me-1"></i>Quay lại
          </router-link>
        </div>
      </div>
      
      <div class="card-body">
        <!-- Thông tin lớp học -->
        <div class="alert alert-info d-flex align-items-center mb-3">
          <i class="bi bi-info-circle-fill me-2"></i>
          <div>
            <strong>Thông tin lớp học:</strong> 
            Số giáo viên phân công giảng dạy: {{ teacherCount }}
          </div>
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
                placeholder="Tìm kiếm giáo viên..." 
                v-model="searchQuery"
                @input="handleSearchInput"
              >
              <button class="btn btn-outline-secondary" type="button" @click="fetchTeachers">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Loading spinner -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Đang tải dữ liệu...</p>
        </div>
        
        <!-- Teachers table -->
        <div v-else-if="teachers.length" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Mã giáo viên</th>
                <th scope="col">Họ và tên</th>
                <th scope="col">Email</th>
                <th scope="col">Số điện thoại</th>
                <th scope="col">Giới tính</th>
                <th scope="col">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(teacher, index) in teachers" :key="teacher.id">
                <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                <td>{{ teacher.id }}</td>
                <td>{{ teacher.last_name }} {{ teacher.first_name }}</td>
                <td>{{ teacher.email }}</td>
                <td>{{ teacher.phone_number }}</td>
                <td>{{ teacher.gender === 'MALE' ? 'Nam' : 'Nữ' }}</td>
                <td>
                  <button @click="confirmRemoveTeacher(teacher)" class="btn btn-sm btn-outline-danger">
                    <i class="bi bi-trash me-1"></i>Xóa khỏi lớp
                  </button>
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
            item-label="giáo viên"
            @page-change="changePage"
            @page-size-change="changePageSize"
          />
        </div>
        
        <!-- No teachers found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Chưa có giáo viên nào được phân công cho lớp học này.</p>
          <button @click="openAddTeacherModal" class="btn btn-primary">
            <i class="bi bi-plus-circle me-1"></i>Thêm Giáo Viên
          </button>
        </div>
      </div>
    </div>
    
    <!-- Modal thêm giáo viên vào lớp -->
    <div class="modal fade" id="addTeacherModal" tabindex="-1" data-bs-backdrop="static" ref="addTeacherModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Thêm Giáo Viên Vào Lớp</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <!-- Tìm kiếm giáo viên -->
            <div class="mb-3">
              <label class="form-label">Tìm kiếm giáo viên</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-search"></i>
                </span>
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Nhập mã, tên giáo viên hoặc email..." 
                  v-model="searchTeacherQuery"
                  @input="searchAvailableTeachers"
                >
              </div>
              <small class="text-muted">Tìm kiếm giáo viên chưa được phân công cho lớp này.</small>
            </div>
            
            <!-- Loading spinner -->
            <div v-if="loadingAvailableTeachers" class="text-center my-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <span class="ms-2">Đang tìm kiếm...</span>
            </div>
            
            <!-- Danh sách giáo viên có thể thêm -->
            <div v-else-if="availableTeachers.length" class="table-responsive">
              <table class="table table-sm table-hover">
                <thead class="table-light">
                  <tr>
                    <th scope="col">Mã GV</th>
                    <th scope="col">Họ và tên</th>
                    <th scope="col">Email</th>
                    <th scope="col">Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="teacher in availableTeachers" :key="teacher.id">
                    <td>{{ teacher.id }}</td>
                    <td>{{ teacher.last_name }} {{ teacher.first_name }}</td>
                    <td>{{ teacher.email }}</td>
                    <td>
                      <button 
                        @click="addTeacherToClass(teacher.id)" 
                        class="btn btn-sm btn-primary" 
                        :disabled="processingAddTeacher"
                      >
                        <span v-if="processingAddTeacher && processingTeacherId === teacher.id" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                        <i v-else class="bi bi-plus-circle me-1"></i>
                        Thêm vào lớp
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- No available teachers found -->
            <div v-else-if="searchTeacherQuery && !loadingAvailableTeachers" class="text-center my-3">
              <i class="bi bi-search fs-4 text-muted"></i>
              <p class="mt-2">Không tìm thấy giáo viên phù hợp.</p>
            </div>
            
            <!-- Initial state -->
            <div v-else-if="!searchTeacherQuery" class="text-center my-3">
              <i class="bi bi-people fs-4 text-muted"></i>
              <p class="mt-2">Nhập thông tin để tìm kiếm giáo viên.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirm Remove Teacher Modal -->
    <div class="modal fade" id="confirmRemoveModal" tabindex="-1" data-bs-backdrop="static" ref="confirmRemoveModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa giáo viên</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa giáo viên <strong>{{ selectedTeacher.id }} - {{ selectedTeacher.last_name }} {{ selectedTeacher.first_name }}</strong> khỏi lớp học này?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="removeTeacherFromClass" :disabled="processingRemove">
              <span v-if="processingRemove" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
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
import { ref, reactive, onMounted, computed } from 'vue';
import axios from 'axios';
import { Modal, Toast } from 'bootstrap';
import Pagination from '@/components/Pagination.vue';

export default {
  name: 'ClassTeachersManagement',
  components: {
    Pagination
  },
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  setup(props) {
    // State
    const loading = ref(true);
    const teachers = ref([]);
    const classInfo = reactive({
      id: null,
      code: '',
      subject_id: null,
      subject_name: '',
      start_date: '',
      end_date: ''
    });
    const teacherCount = ref(0);
    const searchQuery = ref('');
    
    // Pagination state
    const currentPage = ref(1);
    const pageSize = ref(10);
    const totalItems = ref(0);
    const totalPages = ref(0);
    
    // Modal state for adding teachers
    const searchTeacherQuery = ref('');
    const availableTeachers = ref([]);
    const loadingAvailableTeachers = ref(false);
    const processingAddTeacher = ref(false);
    const processingTeacherId = ref(null);
    
    // Modal state for removing teachers
    const selectedTeacher = reactive({
      id: '',
      first_name: '',
      last_name: ''
    });
    const processingRemove = ref(false);
    
    // Toast notification
    const toastTitle = ref('');
    const toastMessage = ref('');
    const toastType = ref('success');
    
    onMounted(() => {
      fetchClassInfo();
      fetchTeachers();
      
      // Initialize Bootstrap components
      setTimeout(() => {
        const toastEl = document.getElementById('notification');
        if (toastEl) {
          new Toast(toastEl);
        }
      }, 200);
    });
    
    // Fetch class information
    const fetchClassInfo = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get(`http://localhost:5000/api/classes/${props.id}`, {
          headers: {
            'Authorization': token
          }
        });
        
        const classData = response.data;
        classInfo.id = classData.id;
        classInfo.code = classData.code;
        classInfo.subject_id = classData.subject_id;
        classInfo.start_date = classData.start_date;
        classInfo.end_date = classData.end_date;
        
        // Fetch subject name if subject_id exists
        if (classData.subject_id) {
          try {
            const subjectResponse = await axios.get(`http://localhost:5000/api/subjects/${classData.subject_id}`, {
              headers: {
                'Authorization': token
              }
            });
            classInfo.subject_name = `${subjectResponse.data.code} - ${subjectResponse.data.name}`;
          } catch (error) {
            console.error('Error fetching subject:', error);
            classInfo.subject_name = 'Không xác định';
          }
        }
      } catch (error) {
        console.error('Error fetching class info:', error);
        showNotification('Lỗi', 'Không thể tải thông tin lớp học', 'error');
      }
    };
    
    // Fetch teachers in class
    const fetchTeachers = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get(`http://localhost:5000/api/class_teachers/class/${props.id}/teachers`, {
          params: {
            page: currentPage.value,
            per_page: pageSize.value,
            query: searchQuery.value || undefined
          },
          headers: {
            'Authorization': token
          }
        });
        
        if (response.data && response.data.items) {
          teachers.value = response.data.items;
          totalItems.value = response.data.pagination.total;
          totalPages.value = response.data.pagination.pages;
          teacherCount.value = response.data.pagination.total;
        } else {
          teachers.value = [];
          totalItems.value = 0;
          totalPages.value = 0;
          teacherCount.value = 0;
        }
      } catch (error) {
        console.error('Error fetching teachers:', error);
        showNotification('Lỗi', 'Không thể tải danh sách giáo viên', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    // Search handling
    const handleSearchInput = () => {
      currentPage.value = 1;
      fetchTeachers();
    };
    
    const changePage = (page) => {
      currentPage.value = page;
      fetchTeachers();
    };
    
    const changePageSize = (size) => {
      pageSize.value = size;
      currentPage.value = 1;
      fetchTeachers();
    };
    
    // Modal functions
    const openAddTeacherModal = () => {
      searchTeacherQuery.value = '';
      availableTeachers.value = [];
      
      const modalElement = document.getElementById('addTeacherModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    // Search for available teachers (not already in the class)
    const searchAvailableTeachers = async () => {
      if (!searchTeacherQuery.value.trim()) {
        availableTeachers.value = [];
        return;
      }
      
      loadingAvailableTeachers.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get('http://localhost:5000/api/teachers', {
          params: {
            query: searchTeacherQuery.value,
            page: 1,
            per_page: 10
          },
          headers: {
            'Authorization': token
          }
        });
        
        if (response.data && response.data.items) {
          const allTeachers = response.data.items;
          
          // Filter out teachers already in the class
          const classTeachersResponse = await axios.get(`http://localhost:5000/api/class_teachers`, {
            params: {
              class_id: props.id
            },
            headers: {
              'Authorization': token
            }
          });
          
          let existingTeacherIds = [];
          if (classTeachersResponse.data && classTeachersResponse.data.items) {
            existingTeacherIds = classTeachersResponse.data.items.map(ct => ct.teacher_id);
          }
          
          availableTeachers.value = allTeachers.filter(teacher => 
            !existingTeacherIds.includes(teacher.id)
          );
        } else {
          availableTeachers.value = [];
        }
      } catch (error) {
        console.error('Error searching available teachers:', error);
        showNotification('Lỗi', 'Không thể tìm kiếm giáo viên', 'error');
      } finally {
        loadingAvailableTeachers.value = false;
      }
    };
    
    // Add teacher to class
    const addTeacherToClass = async (teacherId) => {
      processingAddTeacher.value = true;
      processingTeacherId.value = teacherId;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.post('http://localhost:5000/api/class_teachers', {
          class_id: props.id,
          teacher_id: teacherId
        }, {
          headers: {
            'Authorization': token
          }
        });
        
        // Remove the added teacher from available teachers list
        availableTeachers.value = availableTeachers.value.filter(t => t.id !== teacherId);
        
        // Refresh teachers list
        fetchTeachers();
        
        showNotification('Thành công', 'Đã thêm giáo viên vào lớp học', 'success');
      } catch (error) {
        console.error('Error adding teacher to class:', error);
        let errorMessage = 'Không thể thêm giáo viên vào lớp học';
        
        if (error.response && error.response.data && error.response.data.message) {
          errorMessage = error.response.data.message;
        }
        
        showNotification('Lỗi', errorMessage, 'error');
      } finally {
        processingAddTeacher.value = false;
        processingTeacherId.value = null;
      }
    };
    
    // Confirm remove teacher
    const confirmRemoveTeacher = (teacher) => {
      selectedTeacher.id = teacher.id;
      selectedTeacher.first_name = teacher.first_name;
      selectedTeacher.last_name = teacher.last_name;
      
      const modalElement = document.getElementById('confirmRemoveModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    // Remove teacher from class
    const removeTeacherFromClass = async () => {
      processingRemove.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.delete(`http://localhost:5000/api/class_teachers/${props.id}/${selectedTeacher.id}`, {
          headers: {
            'Authorization': token
          }
        });
        
        // Close modal
        const modalElement = document.getElementById('confirmRemoveModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        // Refresh teachers list
        fetchTeachers();
        
        showNotification('Thành công', 'Đã xóa giáo viên khỏi lớp học', 'success');
      } catch (error) {
        console.error('Error removing teacher from class:', error);
        showNotification('Lỗi', 'Không thể xóa giáo viên khỏi lớp học', 'error');
      } finally {
        processingRemove.value = false;
      }
    };
    
    // Show notification
    const showNotification = (title, message, type) => {
      toastTitle.value = title;
      toastMessage.value = message;
      toastType.value = type;
      
      // Show toast notification
      const toastElement = document.getElementById('notification');
      const toastInstance = Toast.getInstance(toastElement) || new Toast(toastElement);
      toastInstance.show();
    };
    
    return {
      // State
      loading,
      teachers,
      classInfo,
      teacherCount,
      searchQuery,
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      
      // Modal state
      searchTeacherQuery,
      availableTeachers,
      loadingAvailableTeachers,
      processingAddTeacher,
      processingTeacherId,
      selectedTeacher,
      processingRemove,
      
      // Toast
      toastTitle,
      toastMessage,
      toastType,
      
      // Methods
      fetchTeachers,
      handleSearchInput,
      changePage,
      changePageSize,
      openAddTeacherModal,
      searchAvailableTeachers,
      addTeacherToClass,
      confirmRemoveTeacher,
      removeTeacherFromClass
    };
  }
};
</script>

<style scoped>
.class-teachers-management {
  padding: 20px;
}
</style> 
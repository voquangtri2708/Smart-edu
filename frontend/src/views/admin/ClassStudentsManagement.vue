<template>
  <div class="class-students-management">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <div>
          <h4 class="mb-0">Quản Lý Sinh Viên Lớp {{ classInfo.code }}</h4>
          <p class="mb-0 text-muted small">Môn học: {{ classInfo.subject_name || 'Đang tải...' }}</p>
        </div>
        <div>
          <button @click="openAddStudentModal" class="btn btn-primary" :disabled="!canAddMoreStudents">
            <i class="bi bi-plus-circle me-1"></i>Thêm Sinh Viên
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
            Sĩ số tối đa: {{ classInfo.max_student }} 
            | Đã đăng ký: {{ studentCount }}/{{ classInfo.max_student }}
            <span v-if="!canAddMoreStudents" class="text-danger ms-2">(Đã đạt số lượng tối đa)</span>
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
                placeholder="Tìm kiếm sinh viên..." 
                v-model="searchQuery"
                @input="onSearchInput"
              >
              <button class="btn btn-outline-secondary" type="button" @click="fetchStudents">
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
        
        <!-- Students table -->
        <div v-else-if="students.length" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Mã sinh viên</th>
                <th scope="col">Họ và tên</th>
                <th scope="col">Email</th>
                <th scope="col">Số điện thoại</th>
                <th scope="col">Giới tính</th>
                <th scope="col">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(student, index) in students" :key="student.id">
                <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                <td>{{ student.id }}</td>
                <td>{{ student.last_name }} {{ student.first_name }}</td>
                <td>{{ student.email }}</td>
                <td>{{ student.phone_number }}</td>
                <td>{{ student.gender === 'MALE' ? 'Nam' : 'Nữ' }}</td>
                <td>
                  <button @click="confirmRemoveStudent(student)" class="btn btn-sm btn-outline-danger">
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
            item-label="sinh viên"
            @page-change="changePage"
            @page-size-change="changePageSize"
          />
        </div>
        
        <!-- No students found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Chưa có sinh viên nào trong lớp học này.</p>
          <button @click="openAddStudentModal" class="btn btn-primary" :disabled="!canAddMoreStudents">
            <i class="bi bi-plus-circle me-1"></i>Thêm Sinh Viên
          </button>
        </div>
      </div>
    </div>
    
    <!-- Modal thêm sinh viên vào lớp -->
    <div class="modal fade" id="addStudentModal" tabindex="-1" data-bs-backdrop="static" ref="addStudentModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Thêm Sinh Viên Vào Lớp</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="!canAddMoreStudents" class="alert alert-warning">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              Lớp học đã đạt số lượng sinh viên tối đa ({{ classInfo.max_student }} sinh viên).
            </div>
            
            <!-- Tìm kiếm sinh viên -->
            <div class="mb-3">
              <label class="form-label">Tìm kiếm sinh viên</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-search"></i>
                </span>
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Nhập mã, tên sinh viên hoặc email..." 
                  v-model="searchStudentQuery"
                  @input="onSearchStudents"
                >
              </div>
              <small class="text-muted">Tìm kiếm sinh viên chưa đăng ký lớp này.</small>
            </div>
            
            <!-- Loading spinner -->
            <div v-if="loadingAvailableStudents" class="text-center my-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <span class="ms-2">Đang tìm kiếm...</span>
            </div>
            
            <!-- Danh sách sinh viên có thể thêm -->
            <div v-else-if="availableStudents.length" class="table-responsive">
              <table class="table table-sm table-hover">
                <thead class="table-light">
                  <tr>
                    <th scope="col">Mã SV</th>
                    <th scope="col">Họ và tên</th>
                    <th scope="col">Email</th>
                    <th scope="col">Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="student in availableStudents" :key="student.id">
                    <td>{{ student.id }}</td>
                    <td>{{ student.last_name }} {{ student.first_name }}</td>
                    <td>{{ student.email }}</td>
                    <td>
                      <button 
                        @click="addStudentToClass(student.id)" 
                        class="btn btn-sm btn-primary" 
                        :disabled="processingAddStudent || !canAddMoreStudents"
                      >
                        <span v-if="processingAddStudent && processingStudentId === student.id" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                        <i v-else class="bi bi-plus-circle me-1"></i>
                        Thêm vào lớp
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- No available students found -->
            <div v-else-if="searchStudentQuery && !loadingAvailableStudents" class="text-center my-3">
              <i class="bi bi-search fs-4 text-muted"></i>
              <p class="mt-2">Không tìm thấy sinh viên phù hợp.</p>
            </div>
            
            <!-- Initial state -->
            <div v-else-if="!searchStudentQuery" class="text-center my-3">
              <i class="bi bi-people fs-4 text-muted"></i>
              <p class="mt-2">Nhập thông tin để tìm kiếm sinh viên.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirm Remove Student Modal -->
    <div class="modal fade" id="confirmRemoveModal" tabindex="-1" data-bs-backdrop="static" ref="confirmRemoveModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa sinh viên</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa sinh viên <strong>{{ selectedStudent.id }} - {{ selectedStudent.last_name }} {{ selectedStudent.first_name }}</strong> khỏi lớp học này?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="removeStudentFromClass" :disabled="processingRemove">
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
import { debounce } from '@/utils/debounce';

export default {
  name: 'ClassStudentsManagement',
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
    const students = ref([]);
    const classInfo = reactive({
      id: null,
      code: '',
      max_student: 0,
      subject_id: null,
      subject_name: '',
      start_date: '',
      end_date: ''
    });
    const studentCount = ref(0);
    const searchQuery = ref('');
    
    // Pagination state
    const currentPage = ref(1);
    const pageSize = ref(10);
    const totalItems = ref(0);
    const totalPages = ref(0);
    
    // Modal state for adding students
    const searchStudentQuery = ref('');
    const availableStudents = ref([]);
    const loadingAvailableStudents = ref(false);
    const processingAddStudent = ref(false);
    const processingStudentId = ref(null);
    
    // Modal state for removing students
    const selectedStudent = reactive({
      id: '',
      first_name: '',
      last_name: ''
    });
    const processingRemove = ref(false);
    
    // Toast notification
    const toastTitle = ref('');
    const toastMessage = ref('');
    const toastType = ref('success');
    
    // Computed
    const canAddMoreStudents = computed(() => {
      return studentCount.value < classInfo.max_student;
    });
    
    onMounted(() => {
      fetchClassInfo();
      fetchStudents();
      
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
        classInfo.max_student = classData.max_student;
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
    
    // Fetch students in class
    const fetchStudents = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get(`http://localhost:5000/api/class_students/class/${props.id}/students`, {
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
          students.value = response.data.items;
          totalItems.value = response.data.pagination.total;
          totalPages.value = response.data.pagination.pages;
          studentCount.value = response.data.pagination.total;
        } else {
          students.value = [];
          totalItems.value = 0;
          totalPages.value = 0;
          studentCount.value = 0;
        }
      } catch (error) {
        console.error('Error fetching students:', error);
        showNotification('Lỗi', 'Không thể tải danh sách sinh viên', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    // Direct handler for input events
    const onSearchInput = () => {
      debouncedSearch();
    };
    
    const onSearchStudents = () => {
      debouncedSearchStudents();
    };
    
    // Create debounced search functions
    const debouncedSearch = debounce(() => {
      currentPage.value = 1;
      fetchStudents();
    }, 500);
    
    const debouncedSearchStudents = debounce(() => {
      if (!searchStudentQuery.value.trim()) {
        availableStudents.value = [];
        return;
      }
      
      loadingAvailableStudents.value = true;
      searchAvailableStudents();
    }, 500);
    
    const changePage = (page) => {
      currentPage.value = page;
      fetchStudents();
    };
    
    const changePageSize = (size) => {
      pageSize.value = size;
      currentPage.value = 1;
      fetchStudents();
    };
    
    // Modal functions
    const openAddStudentModal = () => {
      searchStudentQuery.value = '';
      availableStudents.value = [];
      
      const modalElement = document.getElementById('addStudentModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    // Search for available students (not already in the class)
    const searchAvailableStudents = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get('http://localhost:5000/api/students', {
          params: {
            query: searchStudentQuery.value,
            page: 1,
            per_page: 10
          },
          headers: {
            'Authorization': token
          }
        });
        
        if (response.data && response.data.items) {
          const allStudents = response.data.items;
          
          // Filter out students already in the class
          const classStudentsResponse = await axios.get(`http://localhost:5000/api/class_students`, {
            params: {
              class_id: props.id
            },
            headers: {
              'Authorization': token
            }
          });
          
          let existingStudentIds = [];
          if (classStudentsResponse.data && classStudentsResponse.data.items) {
            existingStudentIds = classStudentsResponse.data.items.map(cs => cs.student_id);
          }
          
          availableStudents.value = allStudents.filter(student => 
            !existingStudentIds.includes(student.id)
          );
        } else {
          availableStudents.value = [];
        }
      } catch (error) {
        console.error('Error searching available students:', error);
        showNotification('Lỗi', 'Không thể tìm kiếm sinh viên', 'error');
      } finally {
        loadingAvailableStudents.value = false;
      }
    };
    
    // Add student to class
    const addStudentToClass = async (studentId) => {
      if (!canAddMoreStudents.value) {
        showNotification('Cảnh báo', 'Lớp học đã đạt số lượng sinh viên tối đa', 'error');
        return;
      }
      
      processingAddStudent.value = true;
      processingStudentId.value = studentId;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.post('http://localhost:5000/api/class_students', {
          class_id: props.id,
          student_id: studentId
        }, {
          headers: {
            'Authorization': token
          }
        });
        
        // Remove the added student from available students list
        availableStudents.value = availableStudents.value.filter(s => s.id !== studentId);
        
        // Refresh students list
        fetchStudents();
        
        showNotification('Thành công', 'Đã thêm sinh viên vào lớp học', 'success');
      } catch (error) {
        console.error('Error adding student to class:', error);
        let errorMessage = 'Không thể thêm sinh viên vào lớp học';
        
        if (error.response && error.response.data && error.response.data.message) {
          errorMessage = error.response.data.message;
        }
        
        showNotification('Lỗi', errorMessage, 'error');
      } finally {
        processingAddStudent.value = false;
        processingStudentId.value = null;
      }
    };
    
    // Confirm remove student
    const confirmRemoveStudent = (student) => {
      selectedStudent.id = student.id;
      selectedStudent.first_name = student.first_name;
      selectedStudent.last_name = student.last_name;
      
      const modalElement = document.getElementById('confirmRemoveModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    // Remove student from class
    const removeStudentFromClass = async () => {
      processingRemove.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.delete(`http://localhost:5000/api/class_students/${props.id}/${selectedStudent.id}`, {
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
        
        // Refresh students list
        fetchStudents();
        
        showNotification('Thành công', 'Đã xóa sinh viên khỏi lớp học', 'success');
      } catch (error) {
        console.error('Error removing student from class:', error);
        showNotification('Lỗi', 'Không thể xóa sinh viên khỏi lớp học', 'error');
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
      students,
      classInfo,
      studentCount,
      searchQuery,
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      
      // Computed
      canAddMoreStudents,
      
      // Modal state
      searchStudentQuery,
      availableStudents,
      loadingAvailableStudents,
      processingAddStudent,
      processingStudentId,
      selectedStudent,
      processingRemove,
      
      // Toast
      toastTitle,
      toastMessage,
      toastType,
      
      // Methods
      fetchStudents,
      onSearchInput,
      onSearchStudents,
      changePage,
      changePageSize,
      openAddStudentModal,
      searchAvailableStudents,
      addStudentToClass,
      confirmRemoveStudent,
      removeStudentFromClass
    };
  }
};
</script>

<style scoped>
.class-students-management {
  padding: 20px;
}
</style>
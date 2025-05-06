<template>
  <div class="exam-management">
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Quản Lý Đợt Thi</h4>
        <button @click="openCreateModal" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i>Thêm Đợt Thi Mới
        </button>
      </div>
      
      <div class="card-body">
        <div class="row mb-3">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input 
                type="text" 
                class="form-control" 
                placeholder="Tìm kiếm đợt thi..." 
                v-model="searchQuery"
                @input="onSearchInput"
              >
            </div>
          </div>
          
          <div class="col-md-4">
            <select class="form-select" v-model="filterClass" @change="fetchExams">
              <option value="">Tất cả lớp học</option>
              <option v-for="cls in teacherClasses" :key="cls.id" :value="cls.id">
                {{ cls.code }} - {{ cls.subject_name }}
              </option>
            </select>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" v-model="sortBy" @change="fetchExams">
              <option value="exam_date">Ngày thi</option>
              <option value="created_at">Ngày tạo</option>
              <option value="title">Tiêu đề</option>
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
        
        <!-- Exams table -->
        <div v-else-if="exams.length > 0" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col" width="5%">#</th>
                <th scope="col" width="25%">Tiêu đề</th>
                <th scope="col" width="15%">Lớp</th>
                <th scope="col" width="15%">Ngày thi</th>
                <th scope="col" width="15%">Thời gian</th>
                <th scope="col" width="10%">Thời lượng</th>
                <th scope="col" width="15%">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(exam, index) in exams" :key="exam.id">
                <td>{{ index + 1 }}</td>
                <td>{{ exam.title }}</td>
                <td>{{ getClassCode(exam.class_id) }}</td>
                <td>{{ formatDate(exam.exam_date) }}</td>
                <td>{{ exam.exam_start_time }} - {{ exam.exam_end_time }}</td>
                <td>{{ exam.duration_minutes }} phút</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button @click="viewExamDetails(exam)" class="btn btn-outline-info" title="Xem chi tiết">
                      <i class="bi bi-eye"></i>
                    </button>
                    <button @click="editExam(exam)" class="btn btn-outline-primary" title="Sửa đợt thi">
                      <i class="bi bi-pencil-square"></i>
                    </button>
                    <button @click="manageExamQuestions(exam)" class="btn btn-outline-success" title="Quản lý câu hỏi">
                      <i class="bi bi-list-check"></i>
                    </button>
                    <button @click="confirmDelete(exam)" class="btn btn-outline-danger" title="Xóa đợt thi">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- No exams found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Không tìm thấy đợt thi nào.</p>
          <button v-if="searchQuery || filterClass" @click="clearFilters" class="btn btn-outline-secondary mt-2">Xóa bộ lọc</button>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Modal -->
    <div class="modal fade" id="examModal" tabindex="-1" data-bs-backdrop="static" ref="examModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Cập nhật đợt thi' : 'Thêm đợt thi mới' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="isEditing ? updateExam() : createExam()">
              <div class="mb-3">
                <label class="form-label">Tiêu đề <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentExam.title" required>
              </div>
              
              <div class="mb-3">
                  <label class="form-label">Lớp học <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="currentExam.class_id" required>
                    <option value="">-- Chọn lớp học --</option>
                    <option v-for="cls in teacherClasses" :key="cls.id" :value="cls.id">
                      {{ cls.code }} - {{ cls.subject_name }}
                    </option>
                  </select>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Mô tả</label>
                <textarea class="form-control" v-model="currentExam.description" rows="2"></textarea>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Ngày thi <span class="text-danger">*</span></label>
                  <input type="date" class="form-control" v-model="currentExam.exam_date" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Thời lượng (phút) <span class="text-danger">*</span></label>
                  <input type="number" class="form-control" v-model="currentExam.duration_minutes" min="1" required>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Giờ bắt đầu <span class="text-danger">*</span></label>
                  <input type="time" class="form-control" v-model="currentExam.exam_start_time" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Giờ kết thúc <span class="text-danger">*</span></label>
                  <input type="time" class="form-control" v-model="currentExam.exam_end_time" required>
                </div>
              </div>
              
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Hủy</button>
                <button type="submit" class="btn btn-primary" :disabled="processing">
                  <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
                  {{ isEditing ? 'Cập nhật' : 'Tạo mới' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- View Modal -->
    <div class="modal fade" id="viewExamModal" tabindex="-1" ref="viewExamModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Chi tiết đợt thi</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="viewExam">
            <div class="card mb-3">
              <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="mb-0">{{ viewExam.title }}</h5>
                  <span class="badge bg-primary">{{ getClassCode(viewExam.class_id) }}</span>
                </div>
              </div>
              <div class="card-body">
                <p v-if="viewExam.description">{{ viewExam.description }}</p>
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Ngày thi:</strong> {{ formatDate(viewExam.exam_date) }}</p>
                    <p><strong>Thời gian:</strong> {{ viewExam.exam_start_time }} - {{ viewExam.exam_end_time }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Thời lượng:</strong> {{ viewExam.duration_minutes }} phút</p>
                  </div>
                </div>
                
                <div v-if="viewExamQuestions && viewExamQuestions.length > 0" class="mt-3">
                  <h6>Danh sách câu hỏi ({{ viewExamQuestions.length }})</h6>
                  <div class="table-responsive">
                    <table class="table table-bordered table-hover">
                      <thead class="table-light">
                        <tr>
                          <th width="5%">#</th>
                          <th width="60%">Nội dung câu hỏi</th>
                          <th width="15%">Loại câu hỏi</th>
                          <th width="20%">Điểm</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(question, index) in viewExamQuestions" :key="question.id">
                          <td>{{ index + 1 }}</td>
                          <td>{{ question.question_text }}</td>
                          <td>{{ getQuestionTypeText(question.question_type) }}</td>
                          <td>{{ question.points }}</td>
                        </tr>
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colspan="3" class="text-end"><strong>Tổng điểm:</strong></td>
                          <td>{{ getTotalPoints(viewExamQuestions) }}</td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
                
                <div v-else class="alert alert-warning mt-3">
                  <i class="bi bi-exclamation-triangle-fill me-2"></i>
                  Đợt thi này chưa có câu hỏi nào. Vui lòng thêm câu hỏi.
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
            <button type="button" class="btn btn-success" @click="manageExamQuestionsFromView" data-bs-dismiss="modal">
              <i class="bi bi-list-check me-1"></i>Quản lý câu hỏi
            </button>
            <button type="button" class="btn btn-primary" @click="editExamFromView" data-bs-dismiss="modal">
              <i class="bi bi-pencil-square me-1"></i>Chỉnh sửa
            </button>
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
            <p>Bạn có chắc chắn muốn xóa đợt thi này không?</p>
            <div class="alert alert-warning">
              <i class="bi bi-exclamation-triangle-fill me-1"></i>
              Đợt thi sau khi xóa sẽ không thể khôi phục.
            </div>
            <div class="card p-2 bg-light">
              <p class="mb-0 text-truncate">{{ deleteExamTitle }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteExam" :disabled="processing">
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
        <div class="toast-header" :class="{'bg-success text-white': messageType === 'success', 'bg-danger text-white': messageType === 'danger', 'bg-info text-white': messageType === 'info', 'bg-warning text-dark': messageType === 'warning'}">
          <strong class="me-auto">{{ toastTitle }}</strong>
          <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { Modal, Toast } from 'bootstrap';
import api from '@/utils/api';
import { useRouter } from 'vue-router';

export default {
  name: 'TeacherExamManagement',
  setup() {
    const router = useRouter();
    
    // State
    const exams = ref([]);
    const teacherClasses = ref([]);
    const loading = ref(false);
    const processing = ref(false);
    const searchQuery = ref('');
    const filterClass = ref('');
    const sortBy = ref('exam_date');
    const currentExam = ref({
      title: '',
      description: '',
      exam_date: new Date().toISOString().split('T')[0],
      duration_minutes: 60,
      class_id: '',
      exam_start_time: '08:00',
      exam_end_time: '09:00'
    });
    const isEditing = ref(false);
    const viewExam = ref(null);
    const viewExamQuestions = ref([]);
    const deleteExamId = ref(null);
    const deleteExamTitle = ref('');
    const searchTimeout = ref(null);
    
    // Toast notification state
    const message = ref('');
    const messageType = ref('success');
    const toastTitle = ref('Thông báo');
    let toastInstance = null;
    
    // Modal references
    const examModal = ref(null);
    const viewExamModal = ref(null);
    const deleteModal = ref(null);
    
    // Bootstrap modal instances
    let examModalInstance = null;
    let viewExamModalInstance = null;
    let deleteModalInstance = null;
    
    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      examModalInstance = new Modal(examModal.value);
      viewExamModalInstance = new Modal(viewExamModal.value);
      deleteModalInstance = new Modal(deleteModal.value);
      
      // Initialize toast
      const toastEl = document.getElementById('notification');
      if (toastEl) {
        toastInstance = new Toast(toastEl);
      }
      
      await fetchTeacherClasses();
      await fetchExams();
    });
    
    // Methods
    const fetchExams = async () => {
      loading.value = true;
      try {
        let url = '/exams';
        if (filterClass && filterClass.value) {
          url = `/classes/${filterClass.value}/exams`;
        }
        
        const response = await api.get(url);
        exams.value = response.data || [];
        
        // Sort exams if needed
        if (sortBy.value) {
          const sortField = sortBy.value;
          exams.value.sort((a, b) => {
            if (a[sortField] < b[sortField]) return -1;
            if (a[sortField] > b[sortField]) return 1;
            return 0;
          });
        }
        
        // Filter by search query if provided
        if (searchQuery.value.trim()) {
          const query = searchQuery.value.trim().toLowerCase();
          exams.value = exams.value.filter(exam => 
            exam.title.toLowerCase().includes(query) || 
            (exam.description && exam.description.toLowerCase().includes(query))
          );
        }
      } catch (error) {
        console.error('Error fetching exams:', error);
        showMessage('Đã có lỗi xảy ra khi tải dữ liệu đợt thi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        loading.value = false;
      }
    };
    
    const fetchTeacherClasses = async () => {
      try {
        const response = await api.get('/teacher/classes');
        teacherClasses.value = response.data || [];
      } catch (error) {
        console.error('Error fetching teacher classes:', error);
        showMessage('Đã có lỗi xảy ra khi tải dữ liệu lớp học. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      }
    };
    
    const fetchExamQuestions = async (examId) => {
      try {
        const response = await api.get(`/exams/${examId}/questions`);
        return response.data || [];
      } catch (error) {
        console.error('Error fetching exam questions:', error);
        showMessage('Đã có lỗi xảy ra khi tải dữ liệu câu hỏi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
        return [];
      }
    };
    
    const onSearchInput = () => {
      clearTimeout(searchTimeout.value);
      searchTimeout.value = setTimeout(() => {
        fetchExams();
      }, 500);
    };
    
    const clearFilters = () => {
      searchQuery.value = '';
      filterClass.value = '';
      fetchExams();
    };
    
    const openCreateModal = () => {
      isEditing.value = false;
      currentExam.value = {
        title: '',
        description: '',
        exam_date: new Date().toISOString().split('T')[0],
        duration_minutes: 60,
        class_id: '',
        exam_start_time: '08:00',
        exam_end_time: '09:00'
      };
      examModalInstance.show();
    };
    
    const createExam = async () => {
      if (!validateExam()) return;
      
      processing.value = true;
      try {
        const response = await api.post('/exams', currentExam.value);
        examModalInstance.hide();
        
        await fetchExams();
        
        showMessage('Đợt thi đã được tạo thành công!', 'success', 'Thành công');
        
        // Navigate to exam question management
        if (response.data && response.data.id) {
          setTimeout(() => {
            router.push({ 
              name: 'exam-questions', 
              params: { examId: response.data.id } 
            });
          }, 500);
        }
      } catch (error) {
        console.error('Error creating exam:', error);
        showMessage('Đã có lỗi xảy ra khi tạo đợt thi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        processing.value = false;
      }
    };
    
    const editExam = (exam) => {
      isEditing.value = true;
      currentExam.value = { ...exam };
      examModalInstance.show();
    };
    
    const editExamFromView = () => {
      if (viewExam.value) {
        editExam(viewExam.value);
      }
    };
    
    const updateExam = async () => {
      if (!validateExam()) return;
      
      processing.value = true;
      try {
        await api.put(`/exams/${currentExam.value.id}`, currentExam.value);
        examModalInstance.hide();
        
        await fetchExams();
        
        showMessage('Đợt thi đã được cập nhật thành công!', 'success', 'Thành công');
      } catch (error) {
        console.error('Error updating exam:', error);
        showMessage('Đã có lỗi xảy ra khi cập nhật đợt thi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        processing.value = false;
      }
    };
    
    const viewExamDetails = async (exam) => {
      viewExam.value = exam;
      
      // Fetch exam questions
      viewExamQuestions.value = await fetchExamQuestions(exam.id);
      
      viewExamModalInstance.show();
    };
    
    const manageExamQuestions = (exam) => {
      router.push({ 
        name: 'exam-questions', 
        params: { examId: exam.id } 
      });
    };
    
    const manageExamQuestionsFromView = () => {
      if (viewExam.value) {
        manageExamQuestions(viewExam.value);
      }
    };
    
    const confirmDelete = (exam) => {
      deleteExamId.value = exam.id;
      deleteExamTitle.value = exam.title;
      deleteModalInstance.show();
    };
    
    const deleteExam = async () => {
      processing.value = true;
      try {
        await api.delete(`/exams/${deleteExamId.value}`);
        deleteModalInstance.hide();
        
        await fetchExams();
        
        showMessage('Đợt thi đã được xóa thành công!', 'success', 'Thành công');
      } catch (error) {
        console.error('Error deleting exam:', error);
        showMessage('Đã có lỗi xảy ra khi xóa đợt thi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        processing.value = false;
      }
    };
    
    const validateExam = () => {
      // Validate time make sense
      const startTime = currentExam.value.exam_start_time;
      const endTime = currentExam.value.exam_end_time;
      
      if (startTime >= endTime) {
        showMessage('Giờ kết thúc phải sau giờ bắt đầu.', 'warning', 'Cảnh báo');
        return false;
      }
      
      return true;
    };
    
    const getClassCode = (classId) => {
      const cls = teacherClasses.value.find(c => c.id === classId);
      return cls ? cls.code : 'N/A';
    };
    
    const getQuestionTypeText = (type) => {
      const typeMap = {
        'MULTIPLE_CHOICE': 'Trắc nghiệm',
        'TRUE_FALSE': 'Đúng/Sai',
        'ESSAY': 'Tự luận',
        'SHORT_ANSWER': 'Trả lời ngắn'
      };
      return typeMap[type] || type;
    };
    
    const getTotalPoints = (questions) => {
      if (!questions || !questions.length) return 0;
      return questions.reduce((sum, q) => sum + parseFloat(q.points), 0).toFixed(2);
    };
    
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString('vi-VN');
    };
    
    const showMessage = (text, type = 'success', title = 'Thông báo') => {
      message.value = text;
      messageType.value = type;
      toastTitle.value = title;
      
      // Show the toast
      if (!toastInstance) {
        const toastEl = document.getElementById('notification');
        if (toastEl) {
          toastInstance = new Toast(toastEl);
        }
      }
      
      if (toastInstance) {
        toastInstance.show();
      }
      
      // Auto hide after 5 seconds
      setTimeout(() => {
        message.value = '';
      }, 5000);
    };
    
    return {
      exams,
      teacherClasses,
      loading,
      processing,
      searchQuery,
      filterClass,
      sortBy,
      currentExam,
      isEditing,
      viewExam,
      viewExamQuestions,
      deleteExamTitle,
      examModal,
      viewExamModal,
      deleteModal,
      message,
      messageType,
      toastTitle,
      fetchExams,
      onSearchInput,
      clearFilters,
      openCreateModal,
      createExam,
      editExam,
      editExamFromView,
      updateExam,
      viewExamDetails,
      manageExamQuestions,
      manageExamQuestionsFromView,
      confirmDelete,
      deleteExam,
      getClassCode,
      getQuestionTypeText,
      getTotalPoints,
      formatDate,
      showMessage
    };
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  margin-bottom: 1.5rem;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  padding: 0.75rem 1.25rem;
}

.badge {
  font-size: 0.75rem;
  padding: 0.35em 0.65em;
}

.table th {
  font-weight: 600;
}

.text-break {
  word-break: break-word !important;
  overflow-wrap: break-word !important;
}
</style> 
<template>
  <div class="exam-question-manager">
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">
          <router-link :to="{ name: 'teacher-exams' }" class="btn btn-sm btn-outline-secondary me-2">
            <i class="bi bi-arrow-left"></i>
          </router-link>
          Quản Lý Câu Hỏi Đợt Thi
        </h4>
        <button @click="openAddQuestionsModal" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i>Thêm Câu Hỏi
        </button>
      </div>
      
      <div class="card-body">
        <!-- Exam info -->
        <div class="alert alert-info mb-4" v-if="exam">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h5 class="alert-heading mb-1">{{ exam.title }}</h5>
              <p class="mb-0">Ngày thi: {{ formatDate(exam.exam_date) }} | {{ exam.exam_start_time }} - {{ exam.exam_end_time }} | {{ exam.duration_minutes }} phút</p>
            </div>
            <div class="text-end">
              <span class="badge bg-primary fs-6">{{ getTotalPoints() }} / 10 điểm</span>
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
        
        <!-- Exam questions list -->
        <div v-else-if="examQuestions.length > 0">
          <div class="table-responsive">
            <table class="table table-striped table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th scope="col" width="5%">#</th>
                  <th scope="col" width="55%">Nội dung câu hỏi</th>
                  <th scope="col" width="15%">Loại câu hỏi</th>
                  <th scope="col" width="10%">Điểm</th>
                  <th scope="col" width="15%">Thao tác</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(question, index) in examQuestions" :key="question.id">
                  <td>{{ index + 1 }}</td>
                  <td>
                    <div class="d-flex flex-column">
                      <div class="fw-medium text-break mb-1">{{ question.question_text }}</div>
                      <div v-if="question.question_type === 'MULTIPLE_CHOICE'" class="small">
                        <div v-for="(answer, i) in question.answers" :key="i" class="text-muted">
                          <span :class="{'text-success fw-bold': answer.is_correct}">
                            {{ i + 1 }}. {{ answer.answer_text }}
                            <i v-if="answer.is_correct" class="bi bi-check-circle-fill text-success ms-1"></i>
                          </span>
                        </div>
                      </div>
                      <div v-if="question.question_type === 'TRUE_FALSE'" class="small">
                        <div v-for="(answer, i) in question.answers" :key="i" class="text-muted">
                          <span :class="{'text-success fw-bold': answer.is_correct}">
                            {{ answer.answer_text }}
                            <i v-if="answer.is_correct" class="bi bi-check-circle-fill text-success ms-1"></i>
                          </span>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span class="badge" :class="getQuestionTypeBadgeClass(question.question_type)">
                      {{ getQuestionTypeText(question.question_type) }}
                    </span>
                  </td>
                  <td>
                    <div class="input-group input-group-sm">
                      <input 
                        type="number" 
                        class="form-control" 
                        v-model="question.points" 
                        min="0.1" 
                        max="10" 
                        step="0.1"
                        @change="updateQuestionPoints(question)"
                      >
                    </div>
                  </td>
                  <td>
                    <button @click="removeQuestion(question)" class="btn btn-sm btn-outline-danger">
                      <i class="bi bi-trash"></i> Xóa
                    </button>
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="3" class="text-end"><strong>Tổng điểm:</strong></td>
                  <td colspan="2">
                    <strong :class="{'text-danger': getTotalPoints() > 10, 'text-success': getTotalPoints() === 10}">
                      {{ getTotalPoints() }} / 10 điểm
                    </strong>
                    <div v-if="getTotalPoints() > 10" class="text-danger">
                      <small>Tổng điểm vượt quá 10 điểm!</small>
                    </div>
                    <div v-else-if="getTotalPoints() < 10" class="text-warning">
                      <small>Tổng điểm chưa đủ 10 điểm.</small>
                    </div>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
        
        <!-- No questions yet -->
        <div v-else class="text-center my-5">
          <i class="bi bi-question-circle fs-1 text-muted"></i>
          <p class="mt-2">Đợt thi này chưa có câu hỏi nào.</p>
          <button @click="openAddQuestionsModal" class="btn btn-primary mt-2">
            <i class="bi bi-plus-circle me-1"></i>Thêm câu hỏi
          </button>
        </div>
      </div>
    </div>
    
    <!-- Add Questions Modal -->
    <div class="modal fade" id="addQuestionsModal" tabindex="-1" data-bs-backdrop="static" ref="addQuestionsModal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Thêm câu hỏi vào đợt thi</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
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
                    placeholder="Tìm kiếm câu hỏi..." 
                    v-model="searchQuery"
                    @input="searchQuestions"
                  >
                </div>
              </div>
              
              <div class="col-md-4">
                <select class="form-select" v-model="questionTypeFilter" @change="fetchAvailableQuestions">
                  <option value="">Tất cả loại câu hỏi</option>
                  <option value="MULTIPLE_CHOICE">Trắc nghiệm</option>
                  <option value="TRUE_FALSE">Đúng/Sai</option>
                  <option value="ESSAY">Tự luận</option>
                  <option value="SHORT_ANSWER">Trả lời ngắn</option>
                </select>
              </div>
              
              <div class="col-md-2">
                <div class="d-flex justify-content-end">
                  <span class="badge bg-primary p-2">
                    <i class="bi bi-info-circle me-1"></i>Đã chọn: {{ selectedQuestions.length }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Loading spinner -->
            <div v-if="loadingQuestions" class="text-center my-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Đang tải dữ liệu câu hỏi...</p>
            </div>
            
            <!-- Available questions -->
            <div v-else-if="availableQuestions.length > 0" class="table-responsive" style="max-height: 400px; overflow-y: auto;">
              <table class="table table-hover align-middle">
                <thead class="table-light sticky-top">
                  <tr>
                    <th scope="col" width="5%">
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="checkbox" 
                          :checked="isAllSelected" 
                          @change="toggleSelectAll"
                        >
                      </div>
                    </th>
                    <th scope="col" width="65%">Nội dung câu hỏi</th>
                    <th scope="col" width="15%">Loại câu hỏi</th>
                    <th scope="col" width="15%">Điểm</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="question in availableQuestions" :key="question.id">
                    <td>
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="checkbox" 
                          :checked="isSelected(question)" 
                          @change="toggleSelect(question)"
                        >
                      </div>
                    </td>
                    <td>
                      <div class="d-flex flex-column">
                        <div class="fw-medium text-break mb-1">{{ question.question_text }}</div>
                        <div v-if="question.question_type === 'MULTIPLE_CHOICE'" class="small">
                          <div v-for="(answer, i) in question.answers" :key="i" class="text-muted">
                            <span :class="{'text-success fw-bold': answer.is_correct}">
                              {{ i + 1 }}. {{ answer.answer_text }}
                              <i v-if="answer.is_correct" class="bi bi-check-circle-fill text-success ms-1"></i>
                            </span>
                          </div>
                        </div>
                        <div v-if="question.question_type === 'TRUE_FALSE'" class="small">
                          <div v-for="(answer, i) in question.answers" :key="i" class="text-muted">
                            <span :class="{'text-success fw-bold': answer.is_correct}">
                              {{ answer.answer_text }}
                              <i v-if="answer.is_correct" class="bi bi-check-circle-fill text-success ms-1"></i>
                            </span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="badge" :class="getQuestionTypeBadgeClass(question.question_type)">
                        {{ getQuestionTypeText(question.question_type) }}
                      </span>
                    </td>
                    <td>
                      <div class="input-group input-group-sm">
                        <input 
                          type="number" 
                          class="form-control" 
                          v-model="question.points" 
                          min="0.1" 
                          max="10" 
                          step="0.1"
                        >
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- No questions found -->
            <div v-else class="text-center my-5">
              <i class="bi bi-emoji-frown fs-1 text-muted"></i>
              <p class="mt-2">Không tìm thấy câu hỏi nào.</p>
              <button @click="clearFilters" class="btn btn-outline-secondary mt-2">Xóa bộ lọc</button>
            </div>
            
            <!-- Selected questions info -->
            <div v-if="selectedQuestions.length > 0" class="alert alert-info mt-3">
              <div class="d-flex justify-content-between align-items-center">
                <span><strong>Đã chọn {{ selectedQuestions.length }} câu hỏi</strong></span>
                <span>Tổng điểm: <strong>{{ getSelectedTotalPoints() }}</strong></span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="addSelectedQuestions" 
              :disabled="processing || selectedQuestions.length === 0"
            >
              <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
              Thêm câu hỏi
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="removeQuestionModal" tabindex="-1" data-bs-backdrop="static" ref="removeQuestionModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa câu hỏi này khỏi đợt thi?</p>
            <div class="card p-2 bg-light" v-if="questionToRemove">
              <p class="mb-0 text-truncate">{{ questionToRemove.question_text }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="confirmRemoveQuestion" :disabled="processing">
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
import { ref, computed, onMounted } from 'vue';
import { Modal, Toast } from 'bootstrap';
import { useRoute } from 'vue-router';
import api from '@/utils/api';

export default {
  name: 'ExamQuestionManager',
  setup() {
    const route = useRoute();
    const examId = route.params.examId;
    
    // State
    const exam = ref(null);
    const examQuestions = ref([]);
    const availableQuestions = ref([]);
    const selectedQuestions = ref([]);
    const questionToRemove = ref(null);
    const loading = ref(false);
    const loadingQuestions = ref(false);
    const processing = ref(false);
    const searchQuery = ref('');
    const questionTypeFilter = ref('');
    const searchTimeout = ref(null);
    
    // Toast notification state
    const message = ref('');
    const messageType = ref('success');
    const toastTitle = ref('Thông báo');
    let toastInstance = null;
    
    // Modal references
    const addQuestionsModal = ref(null);
    const removeQuestionModal = ref(null);
    
    // Bootstrap modal instances
    let addQuestionsModalInstance = null;
    let removeQuestionModalInstance = null;
    
    // Computed
    const isAllSelected = computed(() => {
      return availableQuestions.value.length > 0 && 
             availableQuestions.value.every(q => isSelected(q));
    });
    
    // Lifecycle hooks
    onMounted(async () => {
      // Initialize Bootstrap modals
      addQuestionsModalInstance = new Modal(addQuestionsModal.value);
      removeQuestionModalInstance = new Modal(removeQuestionModal.value);
      
      // Initialize toast
      const toastEl = document.getElementById('notification');
      if (toastEl) {
        toastInstance = new Toast(toastEl);
      }
      
      await fetchExamDetails();
      await fetchExamQuestions();
    });
    
    // Methods
    const fetchExamDetails = async () => {
      loading.value = true;
      try {
        const response = await api.get(`/exams/${examId}`);
        exam.value = response.data;
      } catch (error) {
        console.error('Error fetching exam details:', error);
        showMessage('Đã có lỗi xảy ra khi tải thông tin đợt thi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        loading.value = false;
      }
    };
    
    const fetchExamQuestions = async () => {
      loading.value = true;
      try {
        const response = await api.get(`/exams/${examId}/questions`);
        examQuestions.value = response.data || [];
      } catch (error) {
        console.error('Error fetching exam questions:', error);
        showMessage('Đã có lỗi xảy ra khi tải danh sách câu hỏi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        loading.value = false;
      }
    };
    
    const openAddQuestionsModal = async () => {
      selectedQuestions.value = [];
      await fetchAvailableQuestions();
      addQuestionsModalInstance.show();
    };
    
    const fetchAvailableQuestions = async () => {
      loadingQuestions.value = true;
      try {
        // Get all questions from question bank
        const response = await api.get('/questions');
        let questions = response.data.questions || [];
        
        // Filter by question type if selected
        if (questionTypeFilter.value) {
          questions = questions.filter(q => q.question_type === questionTypeFilter.value);
        }
        
        // Add default points to each question (will be edited by teacher)
        questions.forEach(q => {
          // Default points based on question type
          let defaultPoints = 1.0;
          if (q.question_type === 'ESSAY') defaultPoints = 2.0;
          if (q.question_type === 'SHORT_ANSWER') defaultPoints = 1.5;
          
          q.points = defaultPoints;
        });
        
        // Filter out questions that are already in the exam
        const existingQuestionIds = examQuestions.value.map(q => q.id);
        availableQuestions.value = questions.filter(q => !existingQuestionIds.includes(q.id));
        
        // Apply search query if any
        if (searchQuery.value.trim()) {
          searchQuestions();
        }
      } catch (error) {
        console.error('Error fetching available questions:', error);
        showMessage('Đã có lỗi xảy ra khi tải danh sách câu hỏi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        loadingQuestions.value = false;
      }
    };
    
    const searchQuestions = () => {
      clearTimeout(searchTimeout.value);
      searchTimeout.value = setTimeout(() => {
        const query = searchQuery.value.trim().toLowerCase();
        
        if (!query) {
          fetchAvailableQuestions();
          return;
        }
        
        availableQuestions.value = availableQuestions.value.filter(question => 
          question.question_text.toLowerCase().includes(query) ||
          (question.answers && question.answers.some(a => a.answer_text.toLowerCase().includes(query)))
        );
      }, 300);
    };
    
    const clearFilters = () => {
      searchQuery.value = '';
      questionTypeFilter.value = '';
      fetchAvailableQuestions();
    };
    
    const isSelected = (question) => {
      return selectedQuestions.value.some(q => q.id === question.id);
    };
    
    const toggleSelect = (question) => {
      if (isSelected(question)) {
        selectedQuestions.value = selectedQuestions.value.filter(q => q.id !== question.id);
      } else {
        selectedQuestions.value.push(question);
      }
    };
    
    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        selectedQuestions.value = [];
      } else {
        selectedQuestions.value = [...availableQuestions.value];
      }
    };
    
    const addSelectedQuestions = async () => {
      if (selectedQuestions.value.length === 0) return;
      
      processing.value = true;
      try {
        // Prepare the questions data for the API
        const questions = selectedQuestions.value.map(q => ({
          question_id: q.id,
          points: parseFloat(q.points)
        }));
        
        // Format the data as expected by the backend
        const data = {
          questions: questions
        };
        
        // Update the exam with the new questions
        await api.put(`/exams/${examId}`, data);
        
        // Close the modal and refresh the exam questions
        addQuestionsModalInstance.hide();
        await fetchExamQuestions();
        
        showMessage('Câu hỏi đã được thêm vào đợt thi thành công!', 'success', 'Thành công');
      } catch (error) {
        console.error('Error adding questions to exam:', error);
        showMessage('Đã có lỗi xảy ra khi thêm câu hỏi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        processing.value = false;
      }
    };
    
    const updateQuestionPoints = async (question) => {
      const points = parseFloat(question.points);
      if (isNaN(points) || points <= 0 || points > 10) {
        showMessage('Điểm của câu hỏi phải lớn hơn 0 và nhỏ hơn hoặc bằng 10', 'warning', 'Cảnh báo');
        return;
      }
      
      try {
        // Format the data as expected by the backend
        const data = {
          questions: [{
            question_id: question.id,
            points: points
          }]
        };
        
        // Update the exam question
        await api.put(`/exams/${examId}`, data);
        
        showMessage('Điểm câu hỏi đã được cập nhật!', 'success', 'Thành công');
      } catch (error) {
        console.error('Error updating question points:', error);
        showMessage('Đã có lỗi xảy ra khi cập nhật điểm. Vui lòng thử lại sau.', 'danger', 'Lỗi');
        await fetchExamQuestions(); // Reload to get the original values
      }
    };
    
    const removeQuestion = (question) => {
      questionToRemove.value = question;
      removeQuestionModalInstance.show();
    };
    
    const confirmRemoveQuestion = async () => {
      if (!questionToRemove.value) return;
      
      processing.value = true;
      try {
        // Get current exam data
        const response = await api.get(`/exams/${examId}`);
        const currentExam = response.data;
        
        // Prepare updated questions data (exclude the question to remove)
        const updatedQuestions = examQuestions.value
          .filter(q => q.id !== questionToRemove.value.id)
          .map(q => ({
            question_id: q.id,
            points: parseFloat(q.points)
          }));
        
        // Update the exam with the filtered questions
        const data = {
          ...currentExam,
          questions: updatedQuestions
        };
        
        await api.put(`/exams/${examId}`, data);
        
        removeQuestionModalInstance.hide();
        await fetchExamQuestions();
        
        showMessage('Câu hỏi đã được xóa khỏi đợt thi!', 'success', 'Thành công');
      } catch (error) {
        console.error('Error removing question:', error);
        showMessage('Đã có lỗi xảy ra khi xóa câu hỏi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        processing.value = false;
        questionToRemove.value = null;
      }
    };
    
    const getTotalPoints = () => {
      if (!examQuestions.value.length) return 0;
      return examQuestions.value
        .reduce((sum, q) => sum + parseFloat(q.points), 0)
        .toFixed(2);
    };
    
    const getSelectedTotalPoints = () => {
      if (!selectedQuestions.value.length) return 0;
      return selectedQuestions.value
        .reduce((sum, q) => sum + parseFloat(q.points), 0)
        .toFixed(2);
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
    
    const getQuestionTypeBadgeClass = (type) => {
      const classMap = {
        'MULTIPLE_CHOICE': 'bg-primary',
        'TRUE_FALSE': 'bg-success',
        'ESSAY': 'bg-info',
        'SHORT_ANSWER': 'bg-warning'
      };
      return classMap[type] || 'bg-secondary';
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
      exam,
      examQuestions,
      availableQuestions,
      selectedQuestions,
      questionToRemove,
      loading,
      loadingQuestions,
      processing,
      searchQuery,
      questionTypeFilter,
      isAllSelected,
      addQuestionsModal,
      removeQuestionModal,
      message,
      messageType,
      toastTitle,
      fetchExamQuestions,
      openAddQuestionsModal,
      fetchAvailableQuestions,
      searchQuestions,
      clearFilters,
      isSelected,
      toggleSelect,
      toggleSelectAll,
      addSelectedQuestions,
      updateQuestionPoints,
      removeQuestion,
      confirmRemoveQuestion,
      getTotalPoints,
      getSelectedTotalPoints,
      getQuestionTypeText,
      getQuestionTypeBadgeClass,
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

.sticky-top {
  z-index: 1020;
  background-color: #f8f9fa;
}
</style> 
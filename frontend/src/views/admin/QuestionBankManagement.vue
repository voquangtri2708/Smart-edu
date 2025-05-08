<template>
  <div class="question-bank-management">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Quản Lý Ngân Hàng Câu Hỏi</h4>
        <button @click="openCreateModal" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i>Thêm Câu Hỏi Mới
        </button>
      </div>
      
      <div class="card-body">
        <!-- Search and filter -->
        <div class="row mb-3">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input 
                type="text" 
                class="form-control" 
                placeholder="Tìm kiếm câu hỏi..." 
                v-model="searchQuery"
                @input="onSearchInput"
              >
              <button class="btn btn-outline-secondary" type="button" @click="searchQuestions">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" v-model="questionType" @change="filterQuestions">
              <option value="">Tất cả loại câu hỏi</option>
              <option value="MULTIPLE_CHOICE">Trắc nghiệm</option>
              <option value="TRUE_FALSE">Đúng/Sai</option>
              <option value="ESSAY">Tự luận</option>
              <option value="SHORT_ANSWER">Trả lời ngắn</option>
            </select>
          </div>
          
          <div class="col-md-2">
            <select class="form-select" v-model="sortBy" @change="sortQuestions">
              <option value="created_at">Thời gian tạo</option>
              <option value="updated_at">Thời gian cập nhật</option>
              <option value="question_type">Loại câu hỏi</option>
            </select>
          </div>
          
          <div class="col-md-2">
            <select class="form-select" v-model="sortOrder" @change="sortQuestions">
              <option value="desc">Mới nhất</option>
              <option value="asc">Cũ nhất</option>
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
        
        <!-- Questions table -->
        <div v-else-if="questions && questions.length" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col" width="5%">#</th>
                <th scope="col" width="50%">Nội dung câu hỏi</th>
                <th scope="col" width="15%">Loại câu hỏi</th>
                <th scope="col" width="15%">Ngày cập nhật</th>
                <th scope="col" width="15%">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(question, index) in questions" :key="question.id">
                <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                <td>
                  <div class="d-flex flex-column">
                    <div class="fw-medium text-break mb-1" style="max-width: 500px;">{{ question.question_text }}</div>
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
                <td>{{ formatDate(question.updated_at) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button @click="openViewModal(question)" class="btn btn-outline-info">
                      <i class="bi bi-eye"></i>
                    </button>
                    <button @click="openEditModal(question)" class="btn btn-outline-primary">
                      <i class="bi bi-pencil-square"></i>
                    </button>
                    <button @click="confirmDelete(question)" class="btn btn-outline-danger">
                      <i class="bi bi-trash"></i>
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
            item-label="câu hỏi"
            @page-change="changePage"
            @page-size-change="changePageSize"
          />
        </div>
        
        <!-- No questions found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Không tìm thấy câu hỏi nào.</p>
          <button @click="clearFilters" class="btn btn-outline-secondary mt-2">Xóa bộ lọc</button>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Modal -->
    <div class="modal fade" id="questionModal" tabindex="-1" data-bs-backdrop="static" ref="questionModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Cập nhật câu hỏi' : 'Thêm câu hỏi mới' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="isEditing ? updateQuestion() : createQuestion()">
              <div class="mb-3">
                <label class="form-label">Nội dung câu hỏi <span class="text-danger">*</span></label>
                <textarea class="form-control" v-model="currentQuestion.question_text" required rows="3"></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Loại câu hỏi <span class="text-danger">*</span></label>
                <select class="form-select" v-model="currentQuestion.question_type" required @change="onQuestionTypeChange">
                  <option value="MULTIPLE_CHOICE">Trắc nghiệm</option>
                  <option value="TRUE_FALSE">Đúng/Sai</option>
                  <option value="ESSAY">Tự luận</option>
                  <option value="SHORT_ANSWER">Trả lời ngắn</option>
                </select>
              </div>
              
              <!-- Các đáp án nếu là câu hỏi trắc nghiệm hoặc đúng/sai -->
              <div v-if="currentQuestion.question_type === 'MULTIPLE_CHOICE'" class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <label class="form-label mb-0">Đáp án <span class="text-danger">*</span></label>
                  <button type="button" class="btn btn-sm btn-outline-secondary" @click="addAnswer">
                    <i class="bi bi-plus"></i> Thêm đáp án
                  </button>
                </div>
                
                <div v-for="(answer, index) in currentQuestion.answers" :key="index" class="input-group mb-2">
                  <div class="input-group-text">
                    <input class="form-check-input mt-0" type="checkbox" :id="'answer-' + index" v-model="answer.is_correct">
                  </div>
                  <input type="text" class="form-control" v-model="answer.answer_text" placeholder="Nhập đáp án...">
                  <button type="button" class="btn btn-outline-danger" @click="removeAnswer(index)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
                
                <div v-if="currentQuestion.answers.length === 0" class="text-danger">
                  Vui lòng thêm ít nhất một đáp án.
                </div>
              </div>
              
              <div v-if="currentQuestion.question_type === 'TRUE_FALSE'" class="mb-3">
                <label class="form-label">Đáp án đúng <span class="text-danger">*</span></label>
                <div class="form-check">
                  <input class="form-check-input" type="radio" name="tfAnswer" id="tfTrue" value="true" v-model="trueFalseValue">
                  <label class="form-check-label" for="tfTrue">Đúng</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="radio" name="tfAnswer" id="tfFalse" value="false" v-model="trueFalseValue">
                  <label class="form-check-label" for="tfFalse">Sai</label>
                </div>
              </div>
              
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Hủy</button>
                <button type="submit" class="btn btn-primary" :disabled="processing || (isMultipleChoiceValid === false)">
                  <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
                  {{ isEditing ? 'Cập nhật' : 'Thêm mới' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- View Modal -->
    <div class="modal fade" id="viewQuestionModal" tabindex="-1" ref="viewQuestionModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Chi tiết câu hỏi</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="viewQuestion">
            <div class="card mb-3">
              <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="badge" :class="getQuestionTypeBadgeClass(viewQuestion.question_type)">
                    {{ getQuestionTypeText(viewQuestion.question_type) }}
                  </span>
                  <small class="text-muted">Cập nhật: {{ formatDate(viewQuestion.updated_at) }}</small>
                </div>
              </div>
              <div class="card-body">
                <h5 class="card-title mb-3">{{ viewQuestion.question_text }}</h5>
                
                <!-- Hiển thị đáp án -->
                <div v-if="viewQuestion.question_type === 'MULTIPLE_CHOICE'">
                  <h6 class="card-subtitle mb-2 text-muted">Đáp án:</h6>
                  <ul class="list-group">
                    <li v-for="(answer, index) in viewQuestion.answers" :key="index" 
                      class="list-group-item" 
                      :class="{'list-group-item-success': answer.is_correct}">
                      {{ answer.answer_text }}
                      <i v-if="answer.is_correct" class="bi bi-check-circle-fill text-success float-end"></i>
                    </li>
                  </ul>
                </div>
                
                <div v-if="viewQuestion.question_type === 'TRUE_FALSE'">
                  <h6 class="card-subtitle mb-2 text-muted">Đáp án:</h6>
                  <ul class="list-group">
                    <li v-for="(answer, index) in viewQuestion.answers" :key="index" 
                      class="list-group-item" 
                      :class="{'list-group-item-success': answer.is_correct}">
                      {{ answer.answer_text }}
                      <i v-if="answer.is_correct" class="bi bi-check-circle-fill text-success float-end"></i>
                    </li>
                  </ul>
                </div>
                
                <div v-if="viewQuestion.question_type === 'ESSAY'">
                  <h6 class="card-subtitle mb-2 text-muted">Loại câu hỏi: Tự luận</h6>
                  <p class="card-text fst-italic">Học sinh sẽ viết câu trả lời dài.</p>
                </div>
                
                <div v-if="viewQuestion.question_type === 'SHORT_ANSWER'">
                  <h6 class="card-subtitle mb-2 text-muted">Loại câu hỏi: Trả lời ngắn</h6>
                  <p class="card-text fst-italic">Học sinh sẽ viết câu trả lời ngắn gọn.</p>
                </div>
              </div>
              <div class="card-footer text-muted">
                <small>Ngày tạo: {{ formatDate(viewQuestion.created_at) }}</small>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
            <button type="button" class="btn btn-primary" @click="openEditModal(viewQuestion)" data-bs-dismiss="modal">
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
            <p>Bạn có chắc chắn muốn xóa câu hỏi này không?</p>
            <div class="alert alert-warning">
              <i class="bi bi-exclamation-triangle-fill me-1"></i>
              Câu hỏi sau khi xóa sẽ không thể khôi phục.
            </div>
            <div class="card p-2 bg-light">
              <p class="mb-0 text-truncate">{{ deleteQuestionText }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteQuestion" :disabled="processing">
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
import Pagination from '@/components/Pagination.vue';
import api from '@/utils/api';
import moment from 'moment';

export default {
  name: 'QuestionBankManagement',
  components: {
    Pagination
  },
  setup() {
    // State
    const questions = ref([]);
    const currentQuestion = ref({
      question_text: '',
      question_type: 'MULTIPLE_CHOICE',
      answers: []
    });
    const viewQuestion = ref(null);
    const correctAnswerIndex = ref(0);
    const trueFalseValue = ref('true');
    const questionType = ref('');
    const searchQuery = ref('');
    const sortBy = ref('updated_at');
    const sortOrder = ref('desc');
    const currentPage = ref(1);
    const pageSize = ref(10);
    const totalItems = ref(0);
    const totalPages = ref(0);
    const loading = ref(false);
    const processing = ref(false);
    const isEditing = ref(false);
    const deleteQuestionId = ref(null);
    const deleteQuestionText = ref('');
    const searchTimeout = ref(null);
    
    // Modal references
    const questionModal = ref(null);
    const viewQuestionModal = ref(null);
    const deleteModal = ref(null);
    
    // Bootstrap modal instances
    let questionModalInstance = null;
    let viewQuestionModalInstance = null;
    let deleteModalInstance = null;
    
    // Add toast notification state
    const message = ref('');
    const messageType = ref('success');
    const toastTitle = ref('Thông báo');
    let toastInstance = null;
    
    const isMultipleChoiceValid = computed(() => {
      if (currentQuestion.value.question_type !== 'MULTIPLE_CHOICE') return true;
      return currentQuestion.value.answers.length > 0;
    });
    
    // Lifecycle hooks
    onMounted(() => {
      fetchQuestions();
      
      // Initialize Bootstrap modals
      questionModalInstance = new Modal(questionModal.value);
      viewQuestionModalInstance = new Modal(viewQuestionModal.value);
      deleteModalInstance = new Modal(deleteModal.value);
      
      // Initialize toast
      const toastEl = document.getElementById('notification');
      if (toastEl) {
        toastInstance = new Toast(toastEl);
      }
    });
    
    // Methods
    const fetchQuestions = async () => {
      loading.value = true;
      try {
        const params = {
          page: currentPage.value,
          per_page: pageSize.value
        };
        
        if (questionType.value) {
          params.type = questionType.value;
        }
        
        // Add search query if exists
        if (searchQuery.value.trim()) {
          const response = await api.get(`/search/questions?q=${encodeURIComponent(searchQuery.value.trim())}`);
          questions.value = response.data.questions || [];
          totalItems.value = response.data.total || 0;
          totalPages.value = response.data.pages || 0;
        } else {
          const response = await api.get('/questions', { params });
          questions.value = response.data.questions || [];
          totalItems.value = response.data.total || 0;
          totalPages.value = response.data.pages || 0;
        }
      } catch (error) {
        console.error('Error fetching questions:', error);
        questions.value = [];
        totalItems.value = 0;
        totalPages.value = 0;
        showMessage('Đã có lỗi xảy ra khi tải dữ liệu. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        loading.value = false;
      }
    };
    
    const searchQuestions = () => {
      currentPage.value = 1;
      fetchQuestions();
    };
    
    const filterQuestions = () => {
      currentPage.value = 1;
      fetchQuestions();
    };
    
    const sortQuestions = () => {
      // In a real implementation, you would send the sort parameters to the backend
      // For now, we'll just refetch with the current parameters
      fetchQuestions();
    };
    
    const onSearchInput = () => {
      clearTimeout(searchTimeout.value);
      searchTimeout.value = setTimeout(() => {
        currentPage.value = 1;
        fetchQuestions();
      }, 500);
    };
    
    const clearFilters = () => {
      searchQuery.value = '';
      questionType.value = '';
      sortBy.value = 'updated_at';
      sortOrder.value = 'desc';
      currentPage.value = 1;
      fetchQuestions();
    };
    
    const changePage = (page) => {
      currentPage.value = page;
      fetchQuestions();
    };
    
    const changePageSize = (size) => {
      pageSize.value = size;
      currentPage.value = 1;
      fetchQuestions();
    };
    
    const openCreateModal = () => {
      isEditing.value = false;
      currentQuestion.value = {
        question_text: '',
        question_type: 'MULTIPLE_CHOICE',
        answers: [
          { answer_text: '', is_correct: false },
          { answer_text: '', is_correct: false }
        ]
      };
      correctAnswerIndex.value = 0;
      trueFalseValue.value = 'true';
      questionModalInstance.show();
    };
    
    const openEditModal = (question) => {
      isEditing.value = true;
      currentQuestion.value = JSON.parse(JSON.stringify(question));
      
      // Set the correct answer index for multiple choice questions
      if (question.question_type === 'MULTIPLE_CHOICE' && question.answers) {
        correctAnswerIndex.value = question.answers.findIndex(a => a.is_correct);
      }
      
      // Set true/false value
      if (question.question_type === 'TRUE_FALSE' && question.answers) {
        const correctAnswer = question.answers.find(a => a.is_correct);
        trueFalseValue.value = correctAnswer && correctAnswer.answer_text.toLowerCase() === 'đúng' ? 'true' : 'false';
      }
      
      questionModalInstance.show();
    };
    
    const openViewModal = (question) => {
      viewQuestion.value = question;
      viewQuestionModalInstance.show();
    };
    
    const confirmDelete = (question) => {
      deleteQuestionId.value = question.id;
      deleteQuestionText.value = question.question_text;
      deleteModalInstance.show();
    };
    
    const onQuestionTypeChange = () => {
      if (currentQuestion.value.question_type === 'MULTIPLE_CHOICE') {
        if (currentQuestion.value.answers.length === 0) {
          currentQuestion.value.answers = [
            { answer_text: '', is_correct: false },
            { answer_text: '', is_correct: false }
          ];
          correctAnswerIndex.value = 0;
        }
      } else if (currentQuestion.value.question_type === 'TRUE_FALSE') {
        currentQuestion.value.answers = [
          { answer_text: 'Đúng', is_correct: trueFalseValue.value === 'true' },
          { answer_text: 'Sai', is_correct: trueFalseValue.value === 'false' }
        ];
      } else {
        // Clear answers for essay and short answer questions
        currentQuestion.value.answers = [];
      }
    };
    
    const addAnswer = () => {
      currentQuestion.value.answers.push({
        answer_text: '',
        is_correct: false
      });
    };
    
    const removeAnswer = (index) => {
      currentQuestion.value.answers.splice(index, 1);
      
      // Adjust correct answer index if needed
      if (index === correctAnswerIndex.value) {
        correctAnswerIndex.value = 0;
      } else if (index < correctAnswerIndex.value) {
        correctAnswerIndex.value--;
      }
    };
    
    const createQuestion = async () => {
      if (!validateQuestion()) return;
      
      processing.value = true;
      try {
        // Sử dụng đáp án đã được đánh dấu từ checkbox
        if (currentQuestion.value.question_type === 'TRUE_FALSE') {
          currentQuestion.value.answers = [
            { answer_text: 'Đúng', is_correct: trueFalseValue.value === 'true' },
            { answer_text: 'Sai', is_correct: trueFalseValue.value === 'false' }
          ];
        }
        
        const response = await api.post('/questions', currentQuestion.value);
        questionModalInstance.hide();
        
        fetchQuestions();
        
        // Show success toast
        showMessage('Câu hỏi đã được tạo thành công!', 'success', 'Thành công');
      } catch (error) {
        console.error('Error creating question:', error);
        showMessage('Đã có lỗi xảy ra khi tạo câu hỏi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        processing.value = false;
      }
    };
    
    const updateQuestion = async () => {
      if (!validateQuestion()) return;
      
      processing.value = true;
      try {
        // Sử dụng đáp án đã được đánh dấu từ checkbox
        if (currentQuestion.value.question_type === 'TRUE_FALSE') {
          currentQuestion.value.answers = [
            { answer_text: 'Đúng', is_correct: trueFalseValue.value === 'true' },
            { answer_text: 'Sai', is_correct: trueFalseValue.value === 'false' }
          ];
        }
        
        const response = await api.put(`/questions/${currentQuestion.value.id}`, currentQuestion.value);
        questionModalInstance.hide();
        
        fetchQuestions();
        
        // Show success toast
        showMessage('Câu hỏi đã được cập nhật thành công!', 'success', 'Thành công');
      } catch (error) {
        console.error('Error updating question:', error);
        showMessage('Đã có lỗi xảy ra khi cập nhật câu hỏi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        processing.value = false;
      }
    };
    
    const deleteQuestion = async () => {
      processing.value = true;
      try {
        await api.delete(`/questions/${deleteQuestionId.value}`);
        deleteModalInstance.hide();
        
        fetchQuestions();
        
        // Show success toast
        showMessage('Câu hỏi đã được xóa thành công!', 'success', 'Thành công');
      } catch (error) {
        console.error('Error deleting question:', error);
        showMessage('Đã có lỗi xảy ra khi xóa câu hỏi. Vui lòng thử lại sau.', 'danger', 'Lỗi');
      } finally {
        processing.value = false;
      }
    };
    
    const validateQuestion = () => {
      if (!currentQuestion.value.question_text.trim()) {
        showMessage('Vui lòng nhập nội dung câu hỏi.', 'warning', 'Cảnh báo');
        return false;
      }
      
      if (currentQuestion.value.question_type === 'MULTIPLE_CHOICE') {
        if (currentQuestion.value.answers.length < 2) {
          showMessage('Vui lòng thêm ít nhất 2 đáp án cho câu hỏi trắc nghiệm.', 'warning', 'Cảnh báo');
          return false;
        }
        
        // Kiểm tra có ít nhất một đáp án đúng
        const hasCorrectAnswer = currentQuestion.value.answers.some(answer => answer.is_correct);
        if (!hasCorrectAnswer) {
          showMessage('Vui lòng chọn ít nhất một đáp án đúng.', 'warning', 'Cảnh báo');
          return false;
        }
        
        for (const answer of currentQuestion.value.answers) {
          if (!answer.answer_text.trim()) {
            showMessage('Vui lòng nhập nội dung cho tất cả các đáp án.', 'warning', 'Cảnh báo');
            return false;
          }
        }
      }
      
      return true;
    };
    
    const formatDate = (dateString) => {
      return moment(dateString).format('DD/MM/YYYY HH:mm');
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
    
    // Add showMessage method
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
      questions,
      currentQuestion,
      viewQuestion,
      correctAnswerIndex,
      trueFalseValue,
      questionType,
      searchQuery,
      sortBy,
      sortOrder,
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      loading,
      processing,
      isEditing,
      deleteQuestionText,
      isMultipleChoiceValid,
      questionModal,
      viewQuestionModal,
      deleteModal,
      fetchQuestions,
      searchQuestions,
      filterQuestions,
      sortQuestions,
      onSearchInput,
      clearFilters,
      changePage,
      changePageSize,
      openCreateModal,
      openEditModal,
      openViewModal,
      confirmDelete,
      onQuestionTypeChange,
      addAnswer,
      removeAnswer,
      createQuestion,
      updateQuestion,
      deleteQuestion,
      formatDate,
      getQuestionTypeText,
      getQuestionTypeBadgeClass,
      message,
      messageType,
      toastTitle,
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
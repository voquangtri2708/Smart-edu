<template>
  <div class="student-exam-result">
    <div class="container mt-4">
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h3>{{ exam.title || 'Kết quả bài kiểm tra' }}</h3>
              <button class="btn btn-outline-primary" @click="goBack">
                <i class="bi bi-arrow-left me-1"></i>Quay lại
              </button>
            </div>
            
            <div class="card-body">
              <!-- Loading spinner -->
              <div v-if="loading" class="d-flex justify-content-center my-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="ms-2">Đang tải kết quả...</p>
              </div>
              
              <!-- Error message -->
              <div v-else-if="error" class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                {{ error }}
              </div>
              
              <!-- Exam results -->
              <div v-else>
                <div class="mb-4">
                  <div class="row">
                    <div class="col-md-6">
                      <p><strong>Lớp:</strong> {{ exam.class_code }}</p>
                      <p><strong>Ngày thi:</strong> {{ formatDate(exam.exam_date) }}</p>
                      <p><strong>Thời gian:</strong> {{ exam.exam_start_time }} - {{ exam.exam_end_time }}</p>
                    </div>
                    <div class="col-md-6">
                      <p><strong>Thời lượng:</strong> {{ exam.duration_minutes }} phút</p>
                      <p><strong>Tổng số câu hỏi:</strong> {{ exam.questions?.length || 0 }}</p>
                      <p><strong>Trạng thái:</strong> <span class="badge bg-info">Đã nộp bài</span></p>
                    </div>
                  </div>
                </div>
                
                <!-- Result summary -->
                <div class="card mb-4">
                  <div class="card-header bg-light">
                    <h5 class="mb-0">Tổng kết</h5>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-4 text-center">
                        <div class="summary-item">
                          <h2 class="text-primary">{{ answeredQuestions }} / {{ exam.questions?.length }}</h2>
                          <p>Số câu đã trả lời</p>
                        </div>
                      </div>
                      <div class="col-md-4 text-center">
                        <div class="summary-item">
                          <h2 class="text-success">{{ correctAnswers }}</h2>
                          <p>Số câu trả lời đúng</p>
                        </div>
                      </div>
                      <div class="col-md-4 text-center">
                        <div class="summary-item">
                          <h2 :class="{'text-success': totalScore >= totalPoints * 0.5, 'text-danger': totalScore < totalPoints * 0.5}">
                            {{ totalScore.toFixed(2) }} / {{ totalPoints.toFixed(2) }}
                          </h2>
                          <p>Tổng điểm</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <hr>
                
                <div v-if="!exam.questions || exam.questions.length === 0" class="alert alert-warning">
                  <i class="bi bi-exclamation-circle me-2"></i>
                  Bài kiểm tra này chưa có câu hỏi nào.
                </div>
                
                <div v-else>
                  <h5 class="mb-3">Chi tiết câu trả lời</h5>
                  
                  <!-- Questions -->
                  <div v-for="(question, index) in exam.questions" :key="question.id" class="card mb-3">
                    <div class="card-header d-flex justify-content-between align-items-center">
                      <h6 class="mb-0">Câu {{ index + 1 }}: ({{ question.points }} điểm)</h6>
                      <div>
                        <span class="badge me-2" :class="getQuestionTypeClass(question.question_type)">
                          {{ getQuestionTypeText(question.question_type) }}
                        </span>
                        <span class="badge" :class="{
                          'bg-success': question.is_correct === true,
                          'bg-danger': question.is_correct === false,
                          'bg-warning': question.is_correct === null && question.student_answer,
                          'bg-secondary': !question.student_answer
                        }">
                          {{ getAnswerStatusText(question) }}
                        </span>
                      </div>
                    </div>
                    <div class="card-body">
                      <p class="question-text">{{ question.question_text }}</p>
                      
                      <!-- Multiple choice question -->
                      <div v-if="question.question_type === 'MULTIPLE_CHOICE'" class="mt-3">
                        <div v-for="answer in question.answers" :key="answer.id" class="form-check mb-2">
                          <input
                            class="form-check-input"
                            type="radio"
                            :checked="question.student_answer == answer.id"
                            disabled
                          >
                          <label class="form-check-label" :class="{
                            'text-success fw-bold': answer.is_correct,
                            'text-danger': !answer.is_correct && question.student_answer == answer.id
                          }">
                            {{ answer.answer_text }}
                            <i v-if="answer.is_correct" class="bi bi-check-circle-fill text-success ms-1"></i>
                            <i v-if="!answer.is_correct && question.student_answer == answer.id" class="bi bi-x-circle-fill text-danger ms-1"></i>
                          </label>
                        </div>
                      </div>
                      
                      <!-- True/False question -->
                      <div v-else-if="question.question_type === 'TRUE_FALSE'" class="mt-3">
                        <div v-for="answer in question.answers" :key="answer.id" class="form-check mb-2">
                          <input
                            class="form-check-input"
                            type="radio"
                            :checked="question.student_answer == answer.id"
                            disabled
                          >
                          <label class="form-check-label" :class="{
                            'text-success fw-bold': answer.is_correct,
                            'text-danger': !answer.is_correct && question.student_answer == answer.id
                          }">
                            {{ answer.answer_text }}
                            <i v-if="answer.is_correct" class="bi bi-check-circle-fill text-success ms-1"></i>
                            <i v-if="!answer.is_correct && question.student_answer == answer.id" class="bi bi-x-circle-fill text-danger ms-1"></i>
                          </label>
                        </div>
                      </div>
                      
                      <!-- Essay question -->
                      <div v-else-if="question.question_type === 'ESSAY'" class="mt-3">
                        <div class="mb-3">
                          <label class="form-label fw-bold">Câu trả lời của bạn:</label>
                          <div class="p-3 border rounded" v-if="question.student_answer">
                            {{ question.student_answer }}
                          </div>
                          <div class="p-3 border rounded text-muted fst-italic" v-else>
                            Chưa có câu trả lời
                          </div>
                        </div>
                        <div v-if="question.score !== null" class="d-flex justify-content-end align-items-center">
                          <span class="me-2">Điểm:</span>
                          <span class="badge bg-primary">{{ question.score }} / {{ question.points }}</span>
                        </div>
                      </div>
                      
                      <!-- Short answer question -->
                      <div v-else-if="question.question_type === 'SHORT_ANSWER'" class="mt-3">
                        <div class="mb-3">
                          <label class="form-label fw-bold">Câu trả lời của bạn:</label>
                          <div class="p-3 border rounded" v-if="question.student_answer">
                            {{ question.student_answer }}
                          </div>
                          <div class="p-3 border rounded text-muted fst-italic" v-else>
                            Chưa có câu trả lời
                          </div>
                        </div>
                        <div v-if="question.score !== null" class="d-flex justify-content-end align-items-center">
                          <span class="me-2">Điểm:</span>
                          <span class="badge bg-primary">{{ question.score }} / {{ question.points }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
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
import { useRouter, useRoute } from 'vue-router';
import api from '@/utils/api';
import { Toast } from 'bootstrap';

export default {
  name: 'StudentExamResultView',
  
  setup() {
    const router = useRouter();
    const route = useRoute();
    const examId = route.params.id;
    
    // State
    const exam = ref({});
    const loading = ref(true);
    const error = ref('');
    
    // Toast notification
    const message = ref('');
    const messageType = ref('success');
    const toastTitle = ref('Thông báo');
    let toastInstance = null;
    
    // Computed properties
    const answeredQuestions = computed(() => {
      if (!exam.value.questions) return 0;
      return exam.value.questions.filter(q => q.student_answer).length;
    });
    
    const correctAnswers = computed(() => {
      if (!exam.value.questions) return 0;
      return exam.value.questions.filter(q => q.is_correct === true).length;
    });
    
    const totalScore = computed(() => {
      if (!exam.value.questions) return 0;
      return exam.value.questions.reduce((sum, q) => sum + (q.score || 0), 0);
    });
    
    const totalPoints = computed(() => {
      if (!exam.value.questions) return 0;
      return exam.value.questions.reduce((sum, q) => sum + q.points, 0);
    });
    
    // Lifecycle hooks
    onMounted(async () => {
      await fetchExamResult();
      
      // Initialize toast
      const toastEl = document.getElementById('notification');
      if (toastEl) {
        toastInstance = new Toast(toastEl);
      }
    });
    
    // Methods
    const fetchExamResult = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        const response = await api.get(`/student/exams/${examId}`);
        exam.value = response.data;
      } catch (error) {
        console.error('Error fetching exam result:', error);
        error.value = error.response?.data?.message || 'Đã xảy ra lỗi khi tải kết quả bài kiểm tra.';
      } finally {
        loading.value = false;
      }
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
    
    const getQuestionTypeClass = (type) => {
      const classMap = {
        'MULTIPLE_CHOICE': 'bg-primary',
        'TRUE_FALSE': 'bg-info',
        'ESSAY': 'bg-warning',
        'SHORT_ANSWER': 'bg-success'
      };
      return classMap[type] || 'bg-secondary';
    };
    
    const getAnswerStatusText = (question) => {
      if (!question.student_answer) {
        return 'Chưa trả lời';
      }
      
      if (['ESSAY', 'SHORT_ANSWER'].includes(question.question_type)) {
        return question.score !== null ? 'Đã chấm điểm' : 'Chờ chấm điểm';
      }
      
      return question.is_correct ? 'Đúng' : 'Sai';
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString('vi-VN', options);
    };
    
    const showMessage = (text, type = 'success', title = 'Thông báo') => {
      message.value = text;
      messageType.value = type;
      toastTitle.value = title;
      
      if (toastInstance) {
        toastInstance.show();
      }
    };
    
    const goBack = () => {
      router.push({ name: 'student-exam-schedule' });
    };
    
    return {
      exam,
      loading,
      error,
      answeredQuestions,
      correctAnswers,
      totalScore,
      totalPoints,
      message,
      messageType,
      toastTitle,
      getQuestionTypeText,
      getQuestionTypeClass,
      getAnswerStatusText,
      formatDate,
      showMessage,
      goBack
    };
  }
};
</script>

<style scoped>
.student-exam-result {
  min-height: 95vh;
  padding-bottom: 2rem;
}

.card {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.card-header {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.question-text {
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.summary-item {
  padding: 15px;
  border-radius: 8px;
  background-color: #f8f9fa;
  transition: transform 0.2s;
}

.summary-item:hover {
  transform: translateY(-5px);
}

.badge {
  font-size: 0.8rem;
  padding: 0.35em 0.65em;
}
</style> 
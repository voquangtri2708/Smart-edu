<template>
  <div class="student-exam-take">
    <div class="container mt-4">
      <!-- FaceRecognition component -->
      <div v-if="requireFaceVerification && !faceVerified" class="row mb-4">
        <div class="col-md-12">
          <FaceRecognition 
            :exam-id="examId" 
            @verification-success="onFaceVerificationSuccess" 
            @verification-cancel="onFaceVerificationCancel" 
          />
        </div>
      </div>
      
      <!-- Exam content -->
      <div v-if="!requireFaceVerification || faceVerified" class="row mb-4">
        <div class="col-md-12">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h3>{{ exam.title || 'Bài kiểm tra' }}</h3>
              <div class="d-flex align-items-center">
                <button class="btn btn-outline-primary me-2" @click="manualSave" title="Lưu bài làm">
                  <i class="bi bi-save me-1"></i>Lưu
                </button>
                <button class="btn btn-outline-secondary me-2" @click="reloadSavedAnswers" title="Tải lại bài làm đã lưu">
                  <i class="bi bi-arrow-clockwise me-1"></i>Tải lại
                </button>
                <span class="badge bg-primary me-2 countdown-badge" :class="{'bg-warning': remainingTime <= 300, 'bg-danger': remainingTime <= 60}">
                  <i class="bi bi-clock me-1"></i>
                  <span id="countdown">{{ formatTime(remainingTime) }}</span>
                </span>
                <button class="btn btn-success" @click="submitExam" :disabled="submitting || !canSubmit">
                  <i class="bi bi-check-circle me-1"></i>Nộp bài
                </button>
              </div>
            </div>
            
            <div class="card-body">
              <!-- Loading spinner -->
              <div v-if="loading" class="d-flex justify-content-center my-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="ms-2">Đang tải bài kiểm tra...</p>
              </div>
              
              <!-- Error message -->
              <div v-else-if="error" class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                {{ error }}
                <div class="mt-3">
                  <button class="btn btn-outline-danger" @click="goBack">
                    <i class="bi bi-arrow-left me-1"></i>Quay lại
                  </button>
                </div>
              </div>
              
              <!-- Exam content -->
              <div v-else>
                <div class="mb-4">
                  <div class="row">
                    <div class="col-md-6">
                      <p><strong>Lớp:</strong> {{ exam.class_code }}</p>
                      <p><strong>Ngày thi:</strong> {{ formatDate(exam.exam_date) }}</p>
                      <p><strong>Thời gian:</strong> {{ exam.start_time || exam.exam_start_time }} - {{ exam.end_time || exam.exam_end_time }}</p>
                    </div>
                    <div class="col-md-6">
                      <p><strong>Thời lượng:</strong> {{ exam.duration_minutes }} phút</p>
                      <p><strong>Tổng số câu hỏi:</strong> {{ exam.questions?.length || 0 }}</p>
                      <p><strong>Trạng thái:</strong> <span class="badge bg-success">Đang làm bài</span></p>
                    </div>
                  </div>
                </div>
                
                <hr>
                
                <div v-if="!exam.questions || exam.questions.length === 0" class="alert alert-warning">
                  <i class="bi bi-exclamation-circle me-2"></i>
                  Bài kiểm tra này chưa có câu hỏi nào.
                </div>
                
                <div v-else>
                  <!-- Question navigation -->
                  <div class="mb-4 question-navigation">
                    <div class="d-flex flex-wrap gap-2">
                      <button 
                        v-for="(question, index) in exam.questions" 
                        :key="question.id"
                        class="btn btn-sm"
                        :class="{
                          'btn-primary': currentQuestionIndex === index,
                          'btn-outline-primary': currentQuestionIndex !== index && isQuestionAnswered(question.id),
                          'btn-outline-secondary': currentQuestionIndex !== index && !isQuestionAnswered(question.id)
                        }"
                        @click="currentQuestionIndex = index"
                      >
                        {{ index + 1 }}
                      </button>
                    </div>
                  </div>
                  
                  <!-- Current question -->
                  <div v-if="currentQuestion" class="question-container">
                    <div class="card">
                      <div class="card-header d-flex justify-content-between">
                        <h5>Câu {{ currentQuestionIndex + 1 }}: ({{ currentQuestion.points }} điểm)</h5>
                        <span class="badge" :class="getQuestionTypeClass(currentQuestion.question_type)">
                          {{ getQuestionTypeText(currentQuestion.question_type) }}
                        </span>
                      </div>
                      <div class="card-body">
                        <p class="question-text">{{ currentQuestion.question_text }}</p>
                        
                        <!-- Multiple choice question -->
                        <div v-if="currentQuestion.question_type === 'MULTIPLE_CHOICE'" class="mt-3">
                          <div v-if="!currentQuestion.answers || currentQuestion.answers.length === 0" class="alert alert-warning">
                            <i class="bi bi-exclamation-circle me-2"></i>
                            Câu hỏi này chưa có đáp án.
                          </div>
                          <div v-else>
                            <div v-for="answer in currentQuestion.answers" :key="answer.id" class="form-check mb-2">
                              <input
                                class="form-check-input"
                                type="radio"
                                :id="`answer-${answer.id}`"
                                :name="`question-${currentQuestion.id}`"
                                :value="answer.id"
                                v-model="userAnswers[currentQuestion.id]"
                              >
                              <label class="form-check-label" :for="`answer-${answer.id}`">
                                {{ answer.text || answer.answer_text }}
                              </label>
                            </div>
                            <!-- Debug info -->
                            <div v-if="DEBUG" class="mt-2 text-muted small">
                              <pre>{{ JSON.stringify(currentQuestion.answers, null, 2) }}</pre>
                            </div>
                          </div>
                        </div>
                        
                        <!-- True/False question -->
                        <div v-else-if="currentQuestion.question_type === 'TRUE_FALSE'" class="mt-3">
                          <div v-if="DEBUG" class="mb-3 p-2 border border-info rounded text-muted small">
                            <div>Debug - Cấu trúc đáp án:</div>
                            <pre>{{ JSON.stringify(currentQuestion.answers, null, 2) }}</pre>
                            <div>Giá trị đã chọn: {{ userAnswers[currentQuestion.id] }}</div>
                          </div>
                          
                          <div v-for="answer in currentQuestion.answers" :key="answer.id" class="form-check mb-2">
                            <input
                              class="form-check-input"
                              type="radio"
                              :id="`answer-tf-${answer.id}`"
                              :name="`question-tf-${currentQuestion.id}`"
                              :value="answer.id"
                              v-model="userAnswers[currentQuestion.id]"
                            >
                            <label class="form-check-label" :for="`answer-tf-${answer.id}`">
                              {{ answer.text || answer.answer_text }}
                            </label>
                          </div>
                        </div>
                        
                        <!-- Essay question -->
                        <div v-else-if="currentQuestion.question_type === 'ESSAY'" class="mt-3">
                          <textarea
                            class="form-control"
                            rows="6"
                            :placeholder="'Nhập câu trả lời của bạn...'"
                            v-model="userAnswers[currentQuestion.id]"
                          ></textarea>
                        </div>
                        
                        <!-- Short answer question -->
                        <div v-else-if="currentQuestion.question_type === 'SHORT_ANSWER'" class="mt-3">
                          <input
                            type="text"
                            class="form-control"
                            :placeholder="'Nhập câu trả lời ngắn của bạn...'"
                            v-model="userAnswers[currentQuestion.id]"
                          >
                        </div>
                      </div>
                    </div>
                    
                    <!-- Navigation buttons -->
                    <div class="d-flex justify-content-between mt-3">
                      <button class="btn btn-secondary" @click="prevQuestion" :disabled="currentQuestionIndex === 0">
                        <i class="bi bi-arrow-left me-1"></i>Câu trước
                      </button>
                      <button class="btn btn-primary" @click="nextQuestion" :disabled="currentQuestionIndex === exam.questions.length - 1">
                        Câu tiếp theo<i class="bi bi-arrow-right ms-1"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Submit Confirmation Modal -->
    <div class="modal fade" id="submitModal" tabindex="-1" aria-hidden="true" ref="submitModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận nộp bài</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn nộp bài? Hãy kiểm tra lại trước khi nộp.</p>
            
            <div class="mt-3">
              <h6>Tổng quan:</h6>
              <ul>
                <li>Tổng số câu hỏi: {{ exam.questions?.length || 0 }}</li>
                <li>Số câu đã trả lời: {{ answeredCount }} / {{ exam.questions?.length || 0 }}</li>
                <li>Số câu chưa trả lời: {{ exam.questions?.length - answeredCount || 0 }}</li>
              </ul>
            </div>
            
            <div v-if="exam.questions?.length - answeredCount > 0" class="alert alert-warning">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              Bạn còn {{ exam.questions?.length - answeredCount }} câu chưa trả lời. Bạn vẫn muốn nộp bài?
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-primary" @click="confirmSubmit" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              Xác nhận nộp bài
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
    
    <!-- Thêm thông báo lưu tự động -->
    <div class="auto-save-notification" v-if="autoSaveNotification">
      <i class="bi bi-check-circle me-1"></i> Đã lưu
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/utils/api';
import { Modal, Toast } from 'bootstrap';
import FaceRecognition from '@/components/student/FaceRecognition.vue';

export default {
  name: 'StudentExamTakeView',
  
  components: {
    FaceRecognition
  },
  
  setup() {
    const router = useRouter();
    const route = useRoute();
    const examId = route.params.id;
    
    // State
    const exam = ref({});
    const loading = ref(true);
    const error = ref('');
    const currentQuestionIndex = ref(0);
    const userAnswers = ref({});
    const submitting = ref(false);
    const remainingTime = ref(0);
    const submitModal = ref(null);
    let submitModalInstance = null;
    let countdownInterval = null;
    
    // Face verification state
    const requireFaceVerification = ref(true); // Set to false if you want to disable face verification
    const faceVerified = ref(false);
    
    // Toast notification
    const message = ref('');
    const messageType = ref('success');
    const toastTitle = ref('Thông báo');
    let toastInstance = null;
    
    // Debug mode
    const DEBUG = ref(false); // Set to true to show debug info
    
    // Thêm biến để quản lý thông báo lưu tự động
    const autoSaveNotification = ref(false);
    let autoSaveTimeout = null;
    
    // Computed properties
    const currentQuestion = computed(() => {
      if (!exam.value.questions || exam.value.questions.length === 0) return null;
      return exam.value.questions[currentQuestionIndex.value];
    });
    
    const answeredCount = computed(() => {
      if (!exam.value.questions) return 0;
      return exam.value.questions.filter(q => userAnswers.value[q.id]).length;
    });
    
    const canSubmit = computed(() => {
      return answeredCount.value > 0;
    });
    
    // Lifecycle hooks
    onMounted(async () => {
      // Only fetch exam after face verification or if verification is not required
      if (!requireFaceVerification.value) {
        await fetchExam();
      }
      
      // Initialize modal
      submitModalInstance = new Modal(document.getElementById('submitModal'));
      
      // Initialize toast
      const toastEl = document.getElementById('notification');
      if (toastEl) {
        toastInstance = new Toast(toastEl);
      }
      
      // Set up beforeunload event to warn user
      window.addEventListener('beforeunload', handleBeforeUnload);
    });
    
    onBeforeUnmount(() => {
      // Clean up
      if (countdownInterval) {
        clearInterval(countdownInterval);
      }
      if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
      }
      // Không xóa localStorage để thời gian làm bài được lưu khi tải lại trang
      window.removeEventListener('beforeunload', handleBeforeUnload);
    });
    
    // Methods
    const fetchExam = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        console.log('Đang tải thông tin bài thi ID:', examId);
        const response = await api.get(`/student/exams/${examId}`);
        console.log('Kết quả API:', response.data);
        
        // Kiểm tra phản hồi từ server
        if (!response.data.success) {
          error.value = response.data.message || 'Đã xảy ra lỗi khi tải bài kiểm tra.';
          return;
        }
        
        exam.value = response.data.exam;
        
        // Kiểm tra trạng thái bài thi
        if (exam.value.status === 'upcoming') {
          error.value = 'Bài kiểm tra này chưa đến thời gian làm bài.';
          return;
        } else if (exam.value.status === 'expired') {
          error.value = 'Bài kiểm tra này đã kết thúc.';
          return;
        } else if (exam.value.status !== 'active') {
          error.value = 'Bài kiểm tra này không trong thời gian làm bài.';
          return;
        }
        
        // Initialize timer
        initializeTimer();
        
        // Khôi phục câu trả lời từ localStorage nếu có
        const hasLocalAnswers = loadAnswersFromLocalStorage();
        
        // Nếu không có câu trả lời từ localStorage, sử dụng câu trả lời từ server
        if (!hasLocalAnswers && exam.value.questions) {
          exam.value.questions.forEach(question => {
            if (question.student_answer) {
              userAnswers.value[question.id] = question.student_answer;
            }
          });
        }
      } catch (error) {
        console.error('Error fetching exam:', error);
        error.value = error.response?.data?.message || 'Đã xảy ra lỗi khi tải bài kiểm tra.';
      } finally {
        loading.value = false;
      }
    };
    
    const initializeTimer = () => {
      if (!exam.value || !exam.value.duration_minutes) {
        console.error('Không tìm thấy thông tin thời lượng bài thi');
        return;
      }
      
      console.log('Khởi tạo bộ đếm thời gian...');
      console.log('Thời lượng bài thi (phút):', exam.value.duration_minutes);
      
      // Chuyển đổi thời lượng từ phút sang giây
      const totalDuration = exam.value.duration_minutes * 60;
      
      // Kiểm tra xem đã lưu thời điểm bắt đầu làm bài chưa
      const examStartKey = `exam_start_${examId}`;
      let startTime = localStorage.getItem(examStartKey);
      const now = new Date().getTime();
      
      if (!startTime) {
        // Nếu chưa có thời điểm bắt đầu, lưu thời điểm hiện tại
        startTime = now;
        localStorage.setItem(examStartKey, startTime);
        remainingTime.value = totalDuration;
      } else {
        // Nếu đã có thời điểm bắt đầu, tính thời gian đã trôi qua
        const elapsedSeconds = Math.floor((now - parseInt(startTime)) / 1000);
        remainingTime.value = Math.max(0, totalDuration - elapsedSeconds);
      }
      
      console.log('Thời gian còn lại (giây):', remainingTime.value);
      
      // Set up countdown
      countdownInterval = setInterval(() => {
        if (remainingTime.value <= 0) {
          clearInterval(countdownInterval);
          showMessage('Thời gian làm bài đã hết! Hệ thống sẽ tự động nộp bài.', 'warning', 'Hết giờ');
          confirmSubmit();
          return;
        }
        
        // Cảnh báo khi còn 5 phút
        if (remainingTime.value === 300) {
          showMessage('Còn 5 phút nữa hết giờ! Vui lòng chuẩn bị nộp bài.', 'warning', 'Sắp hết giờ');
        }
        
        // Cảnh báo khi còn 1 phút
        if (remainingTime.value === 60) {
          showMessage('Còn 1 phút nữa hết giờ! Vui lòng kiểm tra và nộp bài sớm.', 'warning', 'Sắp hết giờ');
        }
        
        remainingTime.value -= 1;
      }, 1000);
    };
    
    const nextQuestion = () => {
      if (currentQuestionIndex.value < exam.value.questions.length - 1) {
        currentQuestionIndex.value++;
      }
    };
    
    const prevQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--;
      }
    };
    
    const isQuestionAnswered = (questionId) => {
      return !!userAnswers.value[questionId];
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
    
    const submitExam = () => {
      submitModalInstance.show();
    };
    
    const confirmSubmit = async () => {
      submitting.value = true;
      
      try {
        // Prepare data for submission
        const answersToSubmit = [];
        
        for (const questionId in userAnswers.value) {
          if (userAnswers.value[questionId]) {
            answersToSubmit.push({
              question_id: parseInt(questionId),
              answer_text: userAnswers.value[questionId]
            });
          }
        }
        
        // Submit answers
        await api.post(`/student/exams/${examId}/submit`, {
          answers: answersToSubmit
        });
        
        // Xóa thời điểm bắt đầu làm bài và câu trả lời khi nộp bài
        localStorage.removeItem(`exam_start_${examId}`);
        localStorage.removeItem(`exam_answers_${examId}`);
        
        // Hide modal
        submitModalInstance.hide();
        
        // Show success message
        showMessage('Bài làm của bạn đã được nộp thành công!', 'success', 'Thành công');
        
        // Redirect to results page
        setTimeout(() => {
          router.push({ name: 'student-exam-result', params: { id: examId } });
        }, 1500);
      } catch (error) {
        console.error('Error submitting exam:', error);
        showMessage(error.response?.data?.message || 'Đã xảy ra lỗi khi nộp bài.', 'danger', 'Lỗi');
        submitting.value = false;
      }
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString('vi-VN', options);
    };
    
    const formatTime = (seconds) => {
      if (seconds <= 0) return '00:00:00';
      
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      
      return [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        secs.toString().padStart(2, '0')
      ].join(':');
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
    
    const handleBeforeUnload = (e) => {
      // Display warning if user tries to leave the page
      const message = 'Bạn có chắc chắn muốn rời khỏi trang này? Dữ liệu bài làm có thể bị mất.';
      e.returnValue = message;
      return message;
    };
    
    // Face verification methods
    const onFaceVerificationSuccess = async (userData) => {
      console.log("Xác thực thành công với:", userData);
      faceVerified.value = true;
      showMessage(`Xác thực thành công! Xin chào, ${userData.first_name} ${userData.last_name}`, 'success', 'Xác thực khuôn mặt');
      await fetchExam();
    };
    
    const onFaceVerificationCancel = () => {
      showMessage('Bạn đã hủy xác thực khuôn mặt. Bạn không thể làm bài thi này.', 'warning', 'Đã hủy');
      setTimeout(() => {
        router.push({ name: 'student-exam-schedule' });
      }, 2000);
    };
    
    // Hàm lưu với thông báo
    const saveAnswersToLocalStorage = () => {
      const answersKey = `exam_answers_${examId}`;
      localStorage.setItem(answersKey, JSON.stringify(userAnswers.value));
      
      // Hiển thị thông báo lưu tự động
      autoSaveNotification.value = true;
      
      // Xóa thông báo sau 2 giây
      if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
      }
      autoSaveTimeout = setTimeout(() => {
        autoSaveNotification.value = false;
      }, 2000);
      
      console.log('Đã lưu câu trả lời vào localStorage');
    };

    const loadAnswersFromLocalStorage = () => {
      const answersKey = `exam_answers_${examId}`;
      const savedAnswers = localStorage.getItem(answersKey);
      if (savedAnswers) {
        try {
          userAnswers.value = JSON.parse(savedAnswers);
          console.log('Đã khôi phục câu trả lời từ localStorage');
          return true;
        } catch (error) {
          console.error('Lỗi khi khôi phục câu trả lời:', error);
        }
      }
      return false;
    };

    // Theo dõi thay đổi câu trả lời để lưu tự động
    watch(userAnswers, () => {
      saveAnswersToLocalStorage();
    }, { deep: true });

    // Thêm nút lưu thủ công và tải lại
    const manualSave = () => {
      saveAnswersToLocalStorage();
      showMessage('Bài làm của bạn đã được lưu thành công!', 'success', 'Đã lưu');
    };

    const reloadSavedAnswers = () => {
      if (loadAnswersFromLocalStorage()) {
        showMessage('Đã tải lại bài làm từ bản lưu.', 'info', 'Đã tải lại');
      } else {
        showMessage('Không tìm thấy bài làm đã lưu.', 'warning', 'Lỗi tải lại');
      }
    };

    return {
      exam,
      loading,
      error,
      currentQuestionIndex,
      currentQuestion,
      userAnswers,
      submitting,
      remainingTime,
      submitModal,
      answeredCount,
      canSubmit,
      message,
      messageType,
      toastTitle,
      examId,
      requireFaceVerification,
      faceVerified,
      onFaceVerificationSuccess,
      onFaceVerificationCancel,
      nextQuestion,
      prevQuestion,
      isQuestionAnswered,
      getQuestionTypeText,
      getQuestionTypeClass,
      submitExam,
      confirmSubmit,
      formatDate,
      formatTime,
      showMessage,
      goBack,
      DEBUG,
      autoSaveNotification,
      manualSave,
      reloadSavedAnswers
    };
  }
};
</script>

<style scoped>
.student-exam-take {
  min-height: 95vh;
  padding-bottom: 2rem;
}

.question-navigation {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.question-text {
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.form-check-label {
  cursor: pointer;
}

.modal-backdrop {
  opacity: 0.7 !important;
}

.countdown-badge {
  font-size: 1rem;
  padding: 8px 12px;
  transition: all 0.3s ease;
}

.countdown-badge.bg-warning {
  animation: pulse 1s infinite;
}

.countdown-badge.bg-danger {
  animation: pulse 0.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.auto-save-notification {
  position: fixed;
  bottom: 20px;
  left: 20px;
  background-color: rgba(40, 167, 69, 0.9);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  z-index: 1050;
  font-size: 14px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
</style> 
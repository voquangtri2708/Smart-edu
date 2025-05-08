<template>
  <div class="student-exam-view">
    <div class="container mt-4">
      <div class="row mb-4">
        <div class="col-md-12">
          <h2 class="mb-3">Lịch kiểm tra</h2>
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <div>
                <button class="btn btn-outline-primary me-2" @click="fetchExams">
                  <i class="bi bi-arrow-clockwise me-1"></i>Làm mới
                </button>
              </div>
            </div>
            
            <div class="card-body">
              <!-- Loading spinner -->
              <div v-if="loading" class="d-flex justify-content-center my-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              
              <!-- No exams message -->
              <div v-else-if="exams.length === 0" class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                Bạn không có bài kiểm tra nào.
              </div>
              
              <!-- Exams list -->
              <div v-else>
                <!-- Upcoming Exams -->
                <div class="mb-4">
                  <h4 class="border-bottom pb-2 text-warning">
                    <i class="bi bi-calendar-event me-2"></i>Sắp tới
                  </h4>
                  <div v-if="upcomingExams.length === 0" class="text-muted fst-italic">
                    Không có bài kiểm tra nào sắp tới.
                  </div>
                  <div v-else class="row">
                    <div v-for="exam in upcomingExams" :key="exam.id" class="col-md-4 mb-3">
                      <div class="card h-100 border-warning">
                        <div class="card-header bg-warning bg-opacity-25 d-flex justify-content-between align-items-center">
                          <span class="fw-bold">{{ exam.title }}</span>
                          <span class="badge bg-warning">Sắp tới</span>
                        </div>
                        <div class="card-body">
                          <p class="card-text">
                            <strong>Lớp:</strong> {{ exam.class_code }}<br>
                            <strong>Ngày thi:</strong> {{ formatDate(exam.exam_date) }}<br>
                            <strong>Thời gian:</strong> {{ exam.start_time || '--' }} - {{ exam.end_time || '--' }}<br>
                            <strong>Thời lượng:</strong> {{ exam.duration_minutes }} phút<br>
                            <strong>Số câu hỏi:</strong> {{ exam.question_count || 'Chưa có' }}
                          </p>
                        </div>
                        <div class="card-footer bg-light">
                          <button class="btn btn-sm btn-outline-warning w-100" disabled>
                            <i class="bi bi-clock me-1"></i>Chưa mở
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Active Exams -->
                <div class="mb-4">
                  <h4 class="border-bottom pb-2 text-success">
                    <i class="bi bi-play-circle me-2"></i>Đang mở
                  </h4>
                  <div v-if="activeExams.length === 0" class="text-muted fst-italic">
                    Không có bài kiểm tra nào đang mở.
                  </div>
                  <div v-else class="row">
                    <div v-for="exam in activeExams" :key="exam.id" class="col-md-4 mb-3">
                      <div class="card h-100 border-success">
                        <div class="card-header bg-success bg-opacity-25 d-flex justify-content-between align-items-center">
                          <span class="fw-bold">{{ exam.title }}</span>
                          <span class="badge bg-success">Đang mở</span>
                        </div>
                        <div class="card-body">
                          <p class="card-text">
                            <strong>Lớp:</strong> {{ exam.class_code }}<br>
                            <strong>Ngày thi:</strong> {{ formatDate(exam.exam_date) }}<br>
                            <strong>Thời gian:</strong> {{ exam.start_time || '--' }} - {{ exam.end_time || '--' }}<br>
                            <strong>Thời lượng:</strong> {{ exam.duration_minutes }} phút<br>
                            <strong>Số câu hỏi:</strong> {{ exam.question_count || 'Chưa có' }}
                          </p>
                        </div>
                        <div class="card-footer bg-light">
                          <button v-if="!exam.has_answered" class="btn btn-sm btn-success w-100" @click="startExam(exam.id)">
                            <i class="bi bi-pencil-square me-1"></i>Bắt đầu làm bài
                          </button>
                          <button v-else class="btn btn-sm btn-outline-success w-100" @click="viewExam(exam.id)">
                            <i class="bi bi-eye me-1"></i>Xem bài đã làm
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Expired Exams -->
                <div class="mb-4">
                  <h4 class="border-bottom pb-2 text-danger">
                    <i class="bi bi-clock-history me-2"></i>Đã kết thúc
                  </h4>
                  <div v-if="expiredExams.length === 0" class="text-muted fst-italic">
                    Không có bài kiểm tra nào đã kết thúc.
                  </div>
                  <div v-else class="row">
                    <div v-for="exam in expiredExams" :key="exam.id" class="col-md-4 mb-3">
                      <div class="card h-100 border-danger">
                        <div class="card-header bg-danger bg-opacity-25 d-flex justify-content-between align-items-center">
                          <span class="fw-bold">{{ exam.title }}</span>
                          <span class="badge bg-danger">Đã kết thúc</span>
                        </div>
                        <div class="card-body">
                          <p class="card-text">
                            <strong>Lớp:</strong> {{ exam.class_code }}<br>
                            <strong>Ngày thi:</strong> {{ formatDate(exam.exam_date) }}<br>
                            <strong>Thời gian:</strong> {{ exam.start_time || '--' }} - {{ exam.end_time || '--' }}<br>
                            <strong>Thời lượng:</strong> {{ exam.duration_minutes }} phút<br>
                            <strong>Số câu hỏi:</strong> {{ exam.question_count || 'Chưa có' }}
                          </p>
                        </div>
                        <div class="card-footer bg-light">
                          <button v-if="exam.has_answered" class="btn btn-sm btn-outline-danger w-100" @click="viewExam(exam.id)">
                            <i class="bi bi-eye me-1"></i>Xem kết quả
                          </button>
                          <button v-else class="btn btn-sm btn-outline-danger w-100" disabled>
                            <i class="bi bi-x-circle me-1"></i>Chưa làm bài
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
  name: 'StudentExamView',
  
  setup() {
    const router = useRouter();
    const route = useRoute();
    const exams = ref([]);
    const loading = ref(false);
    
    // Toast notification
    const message = ref('');
    const messageType = ref('success');
    const toastTitle = ref('Thông báo');
    let toastInstance = null;
    
    // Lifecycle hooks
    onMounted(() => {
      fetchExams();
      
      // Kiểm tra xem có thông báo lỗi từ trang làm bài chuyển về không
      if (route.query.error === 'face_verification_failed') {
        showMessage(
          route.query.message || 'Xác thực khuôn mặt thất bại. Vui lòng đảm bảo bạn đang sử dụng đúng tài khoản của mình.', 
          'danger', 
          'Lỗi xác thực'
        );
        
        // Xóa query params sau khi đã hiển thị thông báo
        router.replace({ name: 'student-exam-schedule' });
      }
      
      // Initialize toast
      const toastEl = document.getElementById('notification');
      if (toastEl) {
        toastInstance = new Toast(toastEl);
      }
    });
    
    // Computed properties
    const upcomingExams = computed(() => {
      return exams.value.filter(exam => exam.status === 'upcoming');
    });
    
    const activeExams = computed(() => {
      return exams.value.filter(exam => exam.status === 'active');
    });
    
    const expiredExams = computed(() => {
      return exams.value.filter(exam => exam.status === 'expired');
    });
    
    // Methods
    const fetchExams = async () => {
      loading.value = true;
      try {
        const response = await api.get('/student/exams');
        if (response.data.success) {
          exams.value = response.data.exams;
        } else {
          showMessage(response.data.message || 'Không thể tải danh sách bài kiểm tra', 'danger', 'Lỗi');
        }
      } catch (error) {
        showMessage('Đã xảy ra lỗi khi tải danh sách bài kiểm tra.', 'danger', 'Lỗi');
        console.error('Error fetching exams:', error);
      } finally {
        loading.value = false;
      }
    };
    
    const startExam = (examId) => {
      router.push({ name: 'student-exam-take', params: { id: examId } });
    };
    
    const viewExam = (examId) => {
      router.push({ name: 'student-exam-result', params: { id: examId } });
    };
    
    const formatDate = (dateString) => {
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
    
    return {
      exams,
      loading,
      upcomingExams,
      activeExams,
      expiredExams,
      message,
      messageType,
      toastTitle,
      fetchExams,
      startExam,
      viewExam,
      formatDate,
      showMessage
    };
  }
};
</script>

<style scoped>
.student-exam-view {
  min-height: 90vh;
  background-color: #f8f9fa;
  padding-bottom: 2rem;
}

.card {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.card-header {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  font-weight: 500;
}

.badge {
  font-size: 0.7rem;
  padding: 0.35em 0.65em;
}
</style> 
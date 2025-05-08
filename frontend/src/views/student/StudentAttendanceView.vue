<template>
  <div class="container-fluid attendance-view">
    <div class="card shadow mb-4">
      <div class="card-header py-3 d-flex justify-content-between align-items-center flex-wrap">
        <h5 class="m-0 font-weight-bold text-primary">
          <i class="bi bi-check-circle-fill me-2"></i>Điểm Danh
        </h5>
      </div>
      
      <div class="card-body">
        <!-- Danh sách phiên điểm danh hiện có -->
        <div v-if="!isLoading">
          <div class="section mb-4">
            <h6 class="mb-3 text-primary">
              <i class="bi bi-calendar-check me-2"></i>Phiên điểm danh đang mở
            </h6>
            
            <div v-if="attendanceSessions.length > 0" class="row">
              <div v-for="session in attendanceSessions" :key="session.attendance_id" class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100 border-left-primary">
                  <div class="card-body">
                    <h6 class="card-title text-primary mb-3">{{ session.class_name }}</h6>
                    
                    <div class="d-flex align-items-center mb-2">
                      <i class="bi bi-calendar-date me-2 text-secondary"></i>
                      <div>
                        <strong>Thứ:</strong> {{ session.schedule_day }}
                      </div>
                    </div>
                    
                    <div class="d-flex align-items-center mb-2">
                      <i class="bi bi-calendar3 me-2 text-secondary"></i>
                      <div>
                        <strong>Ngày:</strong> {{ session.specific_date }}
                      </div>
                    </div>
                    
                    <div class="d-flex align-items-center mb-2">
                      <i class="bi bi-clock me-2 text-secondary"></i>
                      <div>
                        <strong>Giờ học:</strong> {{ session.schedule_time }}
                      </div>
                    </div>
                    
                    <div class="d-flex align-items-center mb-2">
                      <i class="bi bi-hourglass-split me-2 text-secondary"></i>
                      <div>
                        <strong>Thời hạn điểm danh:</strong> {{ formatDateTime(session.end_time) }}
                      </div>
                    </div>
                    
                    <div class="d-flex align-items-center mb-3">
                      <i class="bi bi-exclamation-circle me-2 text-secondary"></i>
                      <div>
                        <strong>Trạng thái:</strong> 
                        <span class="badge bg-danger ms-1">Chưa điểm danh</span>
                      </div>
                    </div>
                    
                    <button 
                      class="btn btn-primary w-100" 
                      @click="openAttendanceModal(session)"
                    >
                      <i class="bi bi-camera me-2"></i>Điểm danh ngay
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              Không có phiên điểm danh nào đang mở.
            </div>
          </div>
          
          <div class="section">
            <h6 class="mb-3 text-primary">
              <i class="bi bi-clock-history me-2"></i>Lịch sử điểm danh
            </h6>
            
            <div class="row mb-4">
              <div class="col-md-6 mb-3 mb-md-0">
                <div class="form-group">
                  <label class="form-label"><i class="bi bi-book me-1"></i>Chọn Lớp Học</label>
                  <select v-model="selectedClass" class="form-select" @change="loadAttendanceHistory">
                    <option value="">-- Tất cả lớp học --</option>
                    <option v-for="class_ in classes" :key="class_.id" :value="class_.id">
                      {{ class_.code }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            
            <div v-if="attendanceHistory.length > 0" class="table-responsive">
              <table class="table table-bordered table-hover">
                <thead class="table-light">
                  <tr>
                    <th>Lớp học</th>
                    <th>Thứ</th>
                    <th>Thời gian lịch học</th>
                    <th>Thời gian điểm danh</th>
                    <th>Trạng thái</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in attendanceHistory" :key="record.id">
                    <td>{{ record.class_name }}</td>
                    <td>{{ record.schedule_day }}</td>
                    <td>{{ record.schedule_time }}</td>
                    <td>{{ formatDateTime(record.attendance_time) }}</td>
                    <td>
                      <span 
                        class="badge" 
                        :class="{
                          'bg-success': record.status === 'PRESENT',
                          'bg-danger': record.status === 'ABSENT',
                          'bg-warning': record.status === 'EXCUSED'
                        }"
                      >
                        {{ getStatusText(record.status) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div v-else class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              Không có lịch sử điểm danh nào.
            </div>
          </div>
        </div>
        
        <div v-else class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Đang tải...</span>
          </div>
          <p class="mt-2">Đang tải dữ liệu điểm danh...</p>
        </div>
      </div>
    </div>
    
    <!-- Modal điểm danh bằng khuôn mặt -->
    <div class="modal fade" id="attendanceModal" tabindex="-1" aria-labelledby="attendanceModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title" id="attendanceModalLabel">
              Điểm danh khuôn mặt
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="!isFaceDetected && !isProcessing">
              <div class="alert alert-info mb-3">
                <i class="bi bi-info-circle me-2"></i>
                Vui lòng đảm bảo khuôn mặt của bạn hiển thị rõ ràng và trong vùng camera.
              </div>
              
              <div class="webcam-container text-center mb-3">
                <video ref="webcam" class="webcam-view" autoplay playsinline width="100%" height="300"></video>
                <canvas ref="canvas" style="display:none;"></canvas>
              </div>
              
              <div class="d-grid">
                <button class="btn btn-primary" @click="captureImage">
                  <i class="bi bi-camera-fill me-2"></i>Chụp ảnh
                </button>
              </div>
            </div>
            
            <div v-else-if="isFaceDetected && !isProcessing" class="text-center">
              <div class="alert alert-success mb-3">
                <i class="bi bi-check-circle me-2"></i>
                Đã chụp ảnh khuôn mặt thành công!
              </div>
              
              <div class="image-preview mb-3">
                <img :src="capturedImage" class="img-fluid border rounded" alt="Khuôn mặt đã chụp" />
              </div>
              
              <div class="d-flex justify-content-center gap-2">
                <button class="btn btn-outline-secondary" @click="retakeImage">
                  <i class="bi bi-arrow-repeat me-2"></i>Chụp lại
                </button>
                <button class="btn btn-primary" @click="submitAttendance">
                  <i class="bi bi-check-lg me-2"></i>Xác nhận điểm danh
                </button>
              </div>
            </div>
            
            <div v-else-if="isProcessing" class="text-center my-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Đang xử lý...</span>
              </div>
              <p class="mt-2">Đang xử lý điểm danh...</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast thông báo -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
      <div id="attendanceToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header" :class="toastType === 'success' ? 'bg-success text-white' : 'bg-danger text-white'">
          <i :class="toastType === 'success' ? 'bi bi-check-circle-fill me-2' : 'bi bi-x-circle-fill me-2'"></i>
          <strong class="me-auto">Thông báo</strong>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
          {{ toastMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '@/utils/api';
import { Modal, Toast } from 'bootstrap';

// State
const isLoading = ref(false);
const attendanceSessions = ref([]);
const classes = ref([]);
const selectedClass = ref('');
const attendanceHistory = ref([]);
const currentSession = ref(null);
const webcam = ref(null);
const canvas = ref(null);
const stream = ref(null);
const capturedImage = ref('');
const isFaceDetected = ref(false);
const isProcessing = ref(false);
const toastMessage = ref('');
const toastType = ref('success');
const publicIP = ref('');

// Modals & Toasts
let attendanceModal = null;
let attendanceToast = null;

// Lifecycle hooks
onMounted(async () => {
  // Khởi tạo Bootstrap components
  attendanceModal = new Modal(document.getElementById('attendanceModal'));
  attendanceToast = new Toast(document.getElementById('attendanceToast'));
  
  // Lấy danh sách các phiên điểm danh đang mở
  await loadAttendanceSessions();
  
  // Lấy danh sách lớp học
  await loadClasses();
  
  // Lấy lịch sử điểm danh
  await loadAttendanceHistory();
  
  // Lấy địa chỉ IP Public
  fetchPublicIP();
});

onUnmounted(() => {
  // Đóng camera khi rời khỏi trang
  stopCamera();
});

// Methods
const loadAttendanceSessions = async () => {
  isLoading.value = true;
  
  try {
    const response = await api.get('/student/attendance-sessions');
    attendanceSessions.value = response.data.attendance_sessions;
  } catch (error) {
    console.error('Error loading attendance sessions:', error);
    showToast('Không thể tải phiên điểm danh', 'error');
  } finally {
    isLoading.value = false;
  }
};

const loadClasses = async () => {
  try {
    const response = await api.get('/student/classes');
    classes.value = response.data;
  } catch (error) {
    console.error('Error loading classes:', error);
    showToast('Không thể tải danh sách lớp học', 'error');
  }
};

const loadAttendanceHistory = async () => {
  try {
    const params = selectedClass.value ? { class_id: selectedClass.value } : {};
    const response = await api.get('/student/attendance-history', { params });
    attendanceHistory.value = response.data.attendance_records;
  } catch (error) {
    console.error('Error loading attendance history:', error);
    showToast('Không thể tải lịch sử điểm danh', 'error');
  }
};

const openAttendanceModal = async (session) => {
  currentSession.value = session;
  isFaceDetected.value = false;
  capturedImage.value = '';
  
  attendanceModal.show();
  
  // Đợi modal hiển thị trước khi khởi tạo camera
  setTimeout(() => {
    initCamera();
  }, 500);
};

const initCamera = async () => {
  try {
    // Dừng camera hiện tại nếu có
    if (stream.value) {
      stopCamera();
    }
    
    // Khởi tạo camera
    stream.value = await navigator.mediaDevices.getUserMedia({ 
      video: true,
      audio: false
    });
    
    // Hiển thị luồng video
    webcam.value.srcObject = stream.value;
  } catch (error) {
    console.error('Error accessing camera:', error);
    showToast('Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập.', 'error');
  }
};

const stopCamera = () => {
  if (stream.value) {
    const tracks = stream.value.getTracks();
    tracks.forEach(track => track.stop());
    stream.value = null;
    
    if (webcam.value) {
      webcam.value.srcObject = null;
    }
  }
};

const captureImage = () => {
  // Chụp ảnh từ webcam
  const video = webcam.value;
  const canvasElement = canvas.value;
  
  if (!video || !canvasElement) return;
  
  // Thiết lập kích thước canvas bằng với video
  canvasElement.width = video.videoWidth;
  canvasElement.height = video.videoHeight;
  
  // Vẽ khung hình hiện tại của video lên canvas
  const context = canvasElement.getContext('2d');
  context.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);
  
  // Chuyển đổi canvas thành dữ liệu hình ảnh
  const imageData = canvasElement.toDataURL('image/jpeg');
  
  // Lưu ảnh đã chụp
  capturedImage.value = imageData;
  isFaceDetected.value = true;
  
  // Tắt camera sau khi chụp
  stopCamera();
};

const retakeImage = () => {
  isFaceDetected.value = false;
  capturedImage.value = '';
  
  // Khởi tạo lại camera khi chụp lại
  initCamera();
};

const fetchPublicIP = async () => {
  try {
    const response = await fetch('https://api.ipify.org?format=json');
    const data = await response.json();
    publicIP.value = data.ip;
    console.log("Public IP:", publicIP.value);
  } catch (error) {
    console.error("Không lấy được IP public:", error);
  }
};

const submitAttendance = async () => {
  if (!currentSession.value || !capturedImage.value) return;
  
  isProcessing.value = true;
  
  try {
    // Chuyển đổi base64 image để gửi lên server
    const base64Image = capturedImage.value.split(',')[1]; // Loại bỏ phần data:image/jpeg;base64,
    
    const response = await api.post('/student/mark-attendance', {
      attendance_id: currentSession.value.attendance_id,
      class_id: currentSession.value.class_id,
      schedule_id: currentSession.value.schedule_id,
      face_image: base64Image,
      public_ip: publicIP.value
    });
    
    showToast('Điểm danh thành công!', 'success');
    
    // Đóng modal và cập nhật lại danh sách
    attendanceModal.hide();
    
    // Refresh danh sách phiên điểm danh và lịch sử
    await loadAttendanceSessions();
    await loadAttendanceHistory();
  } catch (error) {
    console.error('Error submitting attendance:', error);
    showToast(error.response?.data?.message || 'Không thể điểm danh. Vui lòng thử lại.', 'error');
  } finally {
    isProcessing.value = false;
    stopCamera();
  }
};

const formatDateTime = (dateTime) => {
  if (!dateTime) return '';
  const date = new Date(dateTime);
  return date.toLocaleString('vi-VN');
};

const getStatusText = (status) => {
  switch (status) {
    case 'PRESENT': return 'Có mặt';
    case 'ABSENT': return 'Vắng';
    case 'EXCUSED': return 'Có phép';
    default: return status;
  }
};

const showToast = (message, type = 'success') => {
  toastMessage.value = message;
  toastType.value = type;
  attendanceToast.show();
};
</script>

<style scoped>
.attendance-view {
  padding-bottom: 20px;
}

.section {
  margin-bottom: 30px;
}

.border-left-primary {
  border-left: 0.25rem solid #4e73df !important;
}

.form-control:focus, .form-select:focus {
  border-color: #bac8f3;
  box-shadow: 0 0 0 0.25rem rgba(78, 115, 223, 0.25);
}

.webcam-container {
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.webcam-view {
  max-width: 100%;
  border-radius: 8px;
  object-fit: cover;
}

.badge {
  font-size: 0.85em;
  padding: 0.35em 0.65em;
}

.image-preview {
  max-width: 300px;
  margin: 0 auto;
}

.image-preview img {
  border-radius: 8px;
  width: 100%;
}
</style> 
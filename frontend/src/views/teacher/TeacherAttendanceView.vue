<template>
  <div class="container-fluid attendance-view">
    <div class="card shadow mb-4">
      <div class="card-header py-3 d-flex justify-content-between align-items-center flex-wrap">
        <h5 class="m-0 font-weight-bold text-primary">
          <i class="bi bi-check-circle-fill me-2"></i>Quản Lý Điểm Danh
        </h5>
        <div class="btn-group viewToggle">
          <button 
            type="button" 
            class="btn btn-sm" 
            :class="currentTab === 'create' ? 'btn-primary' : 'btn-outline-primary'"
            @click="currentTab = 'create'"
          >
            <i class="bi bi-plus-circle me-1"></i>Tạo Điểm Danh
          </button>
          <button 
            type="button" 
            class="btn btn-sm" 
            :class="currentTab === 'history' ? 'btn-primary' : 'btn-outline-primary'"
            @click="currentTab = 'history'"
          >
            <i class="bi bi-clock-history me-1"></i>Lịch Sử Điểm Danh
          </button>
        </div>
      </div>
      
      <div class="card-body">
        <!-- Tạo điểm danh mới -->
        <div v-if="currentTab === 'create'">
          <div class="row mb-4">
            <div class="col-md-6 mb-3 mb-md-0">
              <div class="form-group">
                <label class="form-label"><i class="bi bi-book me-1"></i>Chọn Lớp Học</label>
                <select v-model="selectedClass" class="form-select" @change="loadSchedulesForClass">
                  <option value="">-- Chọn lớp học --</option>
                  <option v-for="class_ in classes" :key="class_.id" :value="class_.id">
                    {{ class_.code }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="col-md-6 mb-3 mb-md-0" v-if="selectedClass">
              <div class="form-group">
                <label class="form-label"><i class="bi bi-calendar-event me-1"></i>Chọn Lịch Học</label>
                <select v-model="selectedSchedule" class="form-select" @change="scheduleSelected">
                  <option value="">-- Chọn lịch học --</option>
                  <option v-for="schedule in schedules" :key="schedule.id" :value="schedule.id">
                    {{ schedule.day_of_week }} ({{ schedule.start_time }} - {{ schedule.end_time }}) - Ngày {{ schedule.specific_date }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          
          <div v-if="selectedSchedule" class="attendance-form mt-4">
            <div class="card border-left-primary">
              <div class="card-body">
                <h6 class="card-title text-primary">Cài đặt thời gian điểm danh</h6>
                
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">Thời gian bắt đầu</label>
                    <input type="datetime-local" v-model="attendanceStartTime" class="form-control" :min="minStartTime" :max="maxStartTime" @change="validateTime" />
                    <small class="text-muted">Phải sau thời điểm hiện tại</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Thời gian kết thúc</label>
                    <input type="datetime-local" v-model="attendanceEndTime" class="form-control" :min="minEndTime" :max="maxEndTime" @change="validateTime" />
                    <small class="text-muted">Phải sau thời gian bắt đầu và trong khoảng lịch học</small>
                  </div>
                </div>
                
                <div class="form-group mb-3">
                  <label class="form-label">Ghi chú (tùy chọn)</label>
                  <textarea v-model="attendanceNotes" class="form-control" rows="2" placeholder="Nhập ghi chú cho buổi điểm danh này..."></textarea>
                </div>
                
                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                  <button class="btn btn-primary" @click="createAttendanceSession" :disabled="!isFormValid || isCreating">
                    <i class="bi bi-check-circle me-2"></i>
                    <span v-if="!isCreating">Tạo Phiên Điểm Danh</span>
                    <span v-else>
                      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                      Đang xử lý...
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else-if="selectedClass && schedules.length === 0" class="alert alert-info mt-4">
            <i class="bi bi-info-circle me-2"></i>
            Không tìm thấy lịch học nào cho lớp này.
          </div>
          
          <div v-else-if="!selectedClass" class="alert alert-info text-center mt-4">
            <i class="bi bi-arrow-up-circle me-2"></i>
            Vui lòng chọn lớp học để tiếp tục
          </div>
        </div>
        
        <!-- Lịch sử điểm danh -->
        <div v-else-if="currentTab === 'history'">
          <div class="row mb-4">
            <div class="col-md-6 mb-3 mb-md-0">
              <div class="form-group">
                <label class="form-label"><i class="bi bi-book me-1"></i>Chọn Lớp Học</label>
                <select v-model="selectedClassForHistory" class="form-select" @change="loadAttendanceHistory">
                  <option value="">-- Chọn lớp học --</option>
                  <option v-for="class_ in classes" :key="class_.id" :value="class_.id">
                    {{ class_.code }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Hiển thị lịch sử điểm danh -->
          <div v-if="selectedClassForHistory && !isLoading">
            <div v-if="attendanceSessions.length > 0">
              <div class="table-responsive">
                <table class="table table-bordered table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Thứ</th>
                      <th>Ngày</th>
                      <th>Thời gian lịch học</th>
                      <th>Thời gian điểm danh</th>
                      <th>Tổng SV</th>
                      <th>Có mặt</th>
                      <th>Vắng</th>
                      <th>Có phép</th>
                      <th>Tỷ lệ</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="session in attendanceSessions" :key="`${session.schedule_id}-${session.attendance_start}`">
                      <td>{{ session.day_of_week }}</td>
                      <td>{{ session.specific_date }}</td>
                      <td>{{ session.schedule_time }}</td>
                      <td>{{ formatDateTime(session.attendance_start) }}</td>
                      <td>{{ session.total_students }}</td>
                      <td class="text-success">{{ session.present_count }}</td>
                      <td class="text-danger">{{ session.absent_count }}</td>
                      <td class="text-warning">{{ session.excused_count }}</td>
                      <td>
                        <div class="progress" style="height: 20px;">
                          <div class="progress-bar bg-success" 
                            role="progressbar" 
                            :style="`width: ${(session.present_count / session.total_students) * 100}%`" 
                            :aria-valuenow="(session.present_count / session.total_students) * 100" 
                            aria-valuemin="0" 
                            aria-valuemax="100">
                            {{ session.attendance_rate }}
                          </div>
                        </div>
                      </td>
                      <td>
                        <button class="btn btn-sm btn-outline-primary" @click="viewAttendanceDetails(session)">
                          <i class="bi bi-eye me-1"></i>Chi tiết
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div v-else class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              Không tìm thấy phiên điểm danh nào cho lớp này.
            </div>
          </div>
          
          <div v-else-if="isLoading" class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Đang tải...</span>
            </div>
            <p class="mt-2">Đang tải dữ liệu điểm danh...</p>
          </div>
          
          <div v-else class="alert alert-info text-center mt-4">
            <i class="bi bi-arrow-up-circle me-2"></i>
            Vui lòng chọn lớp học để xem lịch sử điểm danh
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal Chi tiết điểm danh -->
    <div class="modal fade" id="attendanceDetailModal" tabindex="-1" aria-labelledby="attendanceDetailModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title" id="attendanceDetailModalLabel">
              Chi tiết điểm danh {{ currentSessionDetail?.day_of_week }} ({{ currentSessionDetail?.schedule_time }})
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="isLoadingDetails" class="text-center my-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Đang tải...</span>
              </div>
              <p class="mt-2">Đang tải chi tiết điểm danh...</p>
            </div>
            
            <div v-else-if="attendanceDetails.length > 0">
              <div class="mb-4">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h6 class="mb-0">Thời gian điểm danh: {{ formatDateTime(currentSessionDetail?.attendance_start) }} đến {{ formatDateTime(currentSessionDetail?.attendance_end) }}</h6>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-success" @click="filterStudents('all')">Tất cả</button>
                    <button class="btn btn-outline-success" @click="filterStudents('PRESENT')">Có mặt</button>
                    <button class="btn btn-outline-danger" @click="filterStudents('ABSENT')">Vắng</button>
                    <button class="btn btn-outline-warning" @click="filterStudents('EXCUSED')">Có phép</button>
                  </div>
                </div>
              </div>
              
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>MSSV</th>
                      <th>Họ và tên</th>
                      <th>Trạng thái</th>
                      <th>Thời gian điểm danh</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="record in filteredAttendanceDetails" :key="record.attendance_id">
                      <td>{{ record.student_id }}</td>
                      <td>{{ record.student_name }}</td>
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
                      <td>{{ record.attendance_time ? formatTime(record.attendance_time) : 'Chưa điểm danh' }}</td>
                      <td>
                        <div class="btn-group">
                          <button class="btn btn-sm" 
                            :class="record.status === 'PRESENT' ? 'btn-success' : 'btn-outline-success'" 
                            @click="updateAttendanceStatus(record.attendance_id, 'PRESENT')">
                            <i class="bi bi-check-circle-fill"></i>
                          </button>
                          <button class="btn btn-sm" 
                            :class="record.status === 'ABSENT' ? 'btn-danger' : 'btn-outline-danger'" 
                            @click="updateAttendanceStatus(record.attendance_id, 'ABSENT')">
                            <i class="bi bi-x-circle-fill"></i>
                          </button>
                          <button class="btn btn-sm" 
                            :class="record.status === 'EXCUSED' ? 'btn-warning' : 'btn-outline-warning'" 
                            @click="updateAttendanceStatus(record.attendance_id, 'EXCUSED')">
                            <i class="bi bi-exclamation-circle-fill"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div v-else class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              Không có dữ liệu điểm danh chi tiết.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
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
import { ref, computed, onMounted } from 'vue';
import api from '@/utils/api';
import { Modal, Toast } from 'bootstrap';

// State
const currentTab = ref('create');
const classes = ref([]);
const schedules = ref([]);
const selectedClass = ref('');
const selectedSchedule = ref('');
const selectedClassForHistory = ref('');
const attendanceStartTime = ref('');
const attendanceEndTime = ref('');
const attendanceNotes = ref('');
const isCreating = ref(false);
const isLoading = ref(false);
const isLoadingDetails = ref(false);
const attendanceSessions = ref([]);
const attendanceDetails = ref([]);
const filteredStatus = ref('all');
const currentSessionDetail = ref(null);
const toastMessage = ref('');
const toastType = ref('success');
const publicIP = ref('');

// Detalhes do registro de presença
let attendanceDetailModal = null;
let attendanceToast = null;

// Computed properties
const minStartTime = computed(() => {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
});

const maxStartTime = computed(() => {
  if (!selectedSchedule.value || !schedules.value.length) return '';
  
  const schedule = schedules.value.find(s => s.id === selectedSchedule.value);
  if (!schedule) return '';
  
  const today = new Date();
  const [hours, minutes] = schedule.end_time.split(':');
  
  today.setHours(hours);
  today.setMinutes(minutes);
  today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
  
  return today.toISOString().slice(0, 16);
});

const minEndTime = computed(() => {
  if (!attendanceStartTime.value) return minStartTime.value;
  return attendanceStartTime.value;
});

const maxEndTime = computed(() => {
  if (!selectedSchedule.value || !schedules.value.length) return '';
  
  const schedule = schedules.value.find(s => s.id === selectedSchedule.value);
  if (!schedule) return '';
  
  const today = new Date();
  const [hours, minutes] = schedule.end_time.split(':');
  
  today.setHours(hours);
  today.setMinutes(minutes);
  today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
  
  return today.toISOString().slice(0, 16);
});

const isFormValid = computed(() => {
  return (
    selectedClass.value && 
    selectedSchedule.value && 
    attendanceStartTime.value && 
    attendanceEndTime.value &&
    new Date(attendanceEndTime.value) > new Date(attendanceStartTime.value)
  );
});

const filteredAttendanceDetails = computed(() => {
  if (filteredStatus.value === 'all') {
    return attendanceDetails.value;
  } else {
    return attendanceDetails.value.filter(record => record.status === filteredStatus.value);
  }
});

// Lifecycle hooks
onMounted(async () => {
  // Khởi tạo Bootstrap components
  attendanceDetailModal = new Modal(document.getElementById('attendanceDetailModal'));
  attendanceToast = new Toast(document.getElementById('attendanceToast'));
  
  // Lấy danh sách lớp học
  await loadClasses();
  
  // Lấy địa chỉ IP Public
  fetchPublicIP();
});

// Methods
const loadClasses = async () => {
  try {
    const response = await api.get('/teacher/classes');
    classes.value = response.data;
  } catch (error) {
    showToast('Không thể tải danh sách lớp học', 'error');
    console.error('Error loading classes:', error);
  }
};

const loadSchedulesForClass = async () => {
  if (!selectedClass.value) {
    schedules.value = [];
    selectedSchedule.value = '';
    return;
  }
  
  try {
    const response = await api.get(`/class/${selectedClass.value}/schedules`);
    schedules.value = response.data;
    
    if (schedules.value.length === 0) {
      showToast('Không có lịch học nào trong ngày hôm nay', 'error');
    }
  } catch (error) {
    showToast('Không thể tải lịch học', 'error');
    console.error('Error loading schedules:', error);
  }
};

const scheduleSelected = () => {
  if (!selectedSchedule.value) return;
  
  // Tìm thông tin lịch học đã chọn
  const schedule = schedules.value.find(s => s.id === selectedSchedule.value);
  if (!schedule) return;
  
  // Thiết lập thời gian mặc định
  const today = new Date();
  
  // Thời gian bắt đầu - mặc định là thời gian hiện tại
  today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
  attendanceStartTime.value = today.toISOString().slice(0, 16);
  
  // Thời gian kết thúc - mặc định là sau 15 phút
  const endTime = new Date(today);
  endTime.setMinutes(endTime.getMinutes() + 15);
  endTime.setMinutes(endTime.getMinutes() - endTime.getTimezoneOffset());
  attendanceEndTime.value = endTime.toISOString().slice(0, 16);
};

const validateTime = () => {
  // Kiểm tra thời gian bắt đầu phải trước thời gian kết thúc
  if (attendanceStartTime.value && attendanceEndTime.value) {
    const startTime = new Date(attendanceStartTime.value);
    const endTime = new Date(attendanceEndTime.value);
    
    if (endTime <= startTime) {
      attendanceEndTime.value = '';
      showToast('Thời gian kết thúc phải sau thời gian bắt đầu', 'error');
    }
  }
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

const createAttendanceSession = async () => {
  if (!isFormValid.value) return;
  
  isCreating.value = true;
  
  try {
    const response = await api.post('/teacher/create-attendance-session', {
      class_id: selectedClass.value,
      schedule_id: selectedSchedule.value,
      start_time: attendanceStartTime.value,
      end_time: attendanceEndTime.value,
      notes: attendanceNotes.value,
      public_ip: publicIP.value
    });
    
    showToast('Đã tạo phiên điểm danh thành công', 'success');
    
    // Reset form
    selectedSchedule.value = '';
    attendanceStartTime.value = '';
    attendanceEndTime.value = '';
    attendanceNotes.value = '';
    
  } catch (error) {
    console.error('Error creating attendance session:', error);
    showToast(error.response?.data?.message || 'Không thể tạo phiên điểm danh', 'error');
  } finally {
    isCreating.value = false;
  }
};

const loadAttendanceHistory = async () => {
  if (!selectedClassForHistory.value) {
    attendanceSessions.value = [];
    return;
  }
  
  isLoading.value = true;
  
  try {
    const response = await api.get(`/teacher/class-attendance/${selectedClassForHistory.value}`);
    attendanceSessions.value = response.data.attendance_sessions;
  } catch (error) {
    console.error('Error loading attendance history:', error);
    showToast('Không thể tải lịch sử điểm danh', 'error');
  } finally {
    isLoading.value = false;
  }
};

const viewAttendanceDetails = async (session) => {
  currentSessionDetail.value = session;
  isLoadingDetails.value = true;
  
  try {
    const response = await api.get(
      `/teacher/attendance-details/${selectedClassForHistory.value}/${session.schedule_id}`, 
      { 
        params: { 
          start_time: session.attendance_start,
          end_time: session.attendance_end
        } 
      }
    );
    
    attendanceDetails.value = response.data.attendance_records;
    attendanceDetailModal.show();
  } catch (error) {
    console.error('Error loading attendance details:', error);
    showToast('Không thể tải chi tiết điểm danh', 'error');
  } finally {
    isLoadingDetails.value = false;
  }
};

const updateAttendanceStatus = async (attendanceId, status) => {
  try {
    await api.put(`/teacher/update-attendance-status/${attendanceId}`, {
      status: status
    });
    
    // Cập nhật trạng thái trong danh sách
    const index = attendanceDetails.value.findIndex(record => record.attendance_id === attendanceId);
    if (index !== -1) {
      attendanceDetails.value[index].status = status;
    }
    
    showToast('Đã cập nhật trạng thái điểm danh', 'success');
    
    // Refresh attendance session list after update
    loadAttendanceHistory();
  } catch (error) {
    console.error('Error updating attendance status:', error);
    showToast('Không thể cập nhật trạng thái điểm danh', 'error');
  }
};

const filterStudents = (status) => {
  filteredStatus.value = status;
};

const formatDateTime = (dateTime) => {
  if (!dateTime) return '';
  const date = new Date(dateTime);
  return date.toLocaleString('vi-VN');
};

const formatTime = (dateTime) => {
  if (!dateTime) return '';
  const date = new Date(dateTime);
  return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
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

.border-left-primary {
  border-left: 0.25rem solid #4e73df !important;
}

.form-control:focus, .form-select:focus {
  border-color: #bac8f3;
  box-shadow: 0 0 0 0.25rem rgba(78, 115, 223, 0.25);
}

.table th {
  font-weight: 500;
}

.badge {
  font-size: 0.85em;
  padding: 0.35em 0.65em;
}

/* Progress bar height */
.progress {
  height: 20px;
  font-size: 0.75rem;
}
</style> 
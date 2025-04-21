<!-- filepath: d:\Code\Smart-edu\frontend\src\views\StudentFeedback.vue -->
<template>
  <div class="container py-4">
    <div class="card shadow-sm mb-4">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Đánh giá giảng viên & phòng học</h4>
        <span class="badge bg-light text-dark">{{ statusMessage }}</span>
      </div>
      <div class="card-body">
        <!-- Chọn lớp học -->
        <div class="form-group mb-4">
          <label for="classSelect" class="form-label">Chọn lớp học</label>
          <select class="form-select" id="classSelect" v-model="selectedClassId" @change="loadData">
            <option value="">-- Chọn lớp học --</option>
            <option v-for="class_ in classes" :key="class_.id" :value="class_.id">
               {{ class_.subject_code }} {{ class_.code }}
            </option>
          </select>
        </div>

        <!-- Hiển thị thông tin về thời gian đánh giá -->
        <div v-if="feedbackAvailability" class="alert" :class="getStatusClass(feedbackAvailability.status)">
          <div class="d-flex align-items-center">
            <i class="bi" :class="getStatusIcon(feedbackAvailability.status)" style="font-size: 1.5rem; margin-right: 10px;"></i>
            <div>
              <h5 class="mb-1">{{ getStatusTitle(feedbackAvailability.status) }}</h5>
              <p class="mb-0">
                <span v-if="feedbackAvailability.status === 'available'">
                  Thời gian đánh giá: {{ formatDate(feedbackAvailability.start_date) }} đến {{ formatDate(feedbackAvailability.end_date) }}
                </span>
                <span v-else-if="feedbackAvailability.status === 'upcoming'">
                  Đánh giá sẽ bắt đầu từ {{ formatDate(feedbackAvailability.start_date) }}
                </span>
                <span v-else>
                  Đánh giá đã kết thúc vào {{ formatDate(feedbackAvailability.end_date) }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <!-- Nav tabs cho đánh giá giảng viên và phòng học -->
        <ul class="nav nav-tabs mb-4" v-if="selectedClassId">
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'teachers' }" href="#" 
              @click.prevent="activeTab = 'teachers'">
              <i class="bi bi-person-video3 me-1"></i> Đánh giá giảng viên
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'classrooms' }" href="#" 
              @click.prevent="activeTab = 'classrooms'">
              <i class="bi bi-building me-1"></i> Đánh giá phòng học
            </a>
          </li>
        </ul>

        <!-- Tab nội dung đánh giá giảng viên -->
        <div v-if="selectedClassId && activeTab === 'teachers'">
          <div v-if="loadingTeachers" class="d-flex justify-content-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          <div v-else-if="teachers.length">
            <div class="row row-cols-1 row-cols-md-2 g-4">
              <div v-for="teacher in teachers" :key="teacher.id" class="col">
                <div class="card h-100 border-0 shadow-sm hover-card">
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                      <div class="avatar-placeholder me-3">
                        <span>{{ getInitials(teacher.first_name, teacher.last_name) }}</span>
                      </div>
                      <div>
                        <h5 class="card-title mb-1">{{ teacher.first_name }} {{ teacher.last_name }}</h5>
                        <p class="card-subtitle text-muted small mb-0">
                          <i class="bi bi-envelope me-1"></i> {{ teacher.email }}
                        </p>
                      </div>
                    </div>
                    <div class="form-floating mb-3">
                      <textarea 
                        class="form-control" 
                        :id="`teacherFeedback-${teacher.id}`"
                        v-model="feedbackContent.teachers[teacher.id]" 
                        placeholder="Nhập đánh giá của bạn" 
                        style="height: 120px"
                        :disabled="!canFeedback"
                      ></textarea>
                      <label :for="`teacherFeedback-${teacher.id}`">Nội dung đánh giá</label>
                    </div>
                    <button 
                      class="btn btn-primary w-100" 
                      @click="submitTeacherFeedback(teacher.id)"
                      :disabled="!canFeedback || !feedbackContent.teachers[teacher.id]"
                    >
                      <i class="bi bi-send me-1"></i> {{ getButtonText() }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> {{ getNoTeacherMessage() }}
          </div>
        </div>

        <!-- Tab nội dung đánh giá phòng học -->
        <div v-if="selectedClassId && activeTab === 'classrooms'">
          <div v-if="loadingClassrooms" class="d-flex justify-content-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          <div v-else-if="classrooms.length">
            <div class="row row-cols-1 row-cols-md-2 g-4">
              <div v-for="classroom in classrooms" :key="classroom.id" class="col">
                <div class="card h-100 border-0 shadow-sm hover-card">
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                      <div class="room-placeholder me-3">
                        <i class="bi bi-building"></i>
                      </div>
                      <div>
                        <h5 class="card-title mb-1">Phòng {{ classroom.room_number }}</h5>
                        <p class="card-subtitle text-muted small mb-0">
                          <i class="bi bi-people me-1"></i> Sức chứa: {{ classroom.capacity }} người
                        </p>
                      </div>
                    </div>
                    <div class="form-floating mb-3">
                      <textarea 
                        class="form-control" 
                        :id="`classroomFeedback-${classroom.id}`"
                        v-model="feedbackContent.classrooms[classroom.id]" 
                        placeholder="Nhập đánh giá của bạn" 
                        style="height: 120px"
                        :disabled="!canFeedback"
                      ></textarea>
                      <label :for="`classroomFeedback-${classroom.id}`">Nội dung đánh giá</label>
                    </div>
                    <button 
                      class="btn btn-primary w-100" 
                      @click="submitClassroomFeedback(classroom.id)"
                      :disabled="!canFeedback || !feedbackContent.classrooms[classroom.id]"
                    >
                      <i class="bi bi-send me-1"></i> {{ getButtonText() }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> {{ getNoClassroomMessage() }}
          </div>
        </div>
      </div>
    </div>

    <!-- Toast notification -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
      <div 
        class="toast align-items-center text-white border-0" 
        :class="`bg-${messageType}`"
        role="alert" 
        aria-live="assertive" 
        aria-atomic="true"
        ref="toast"
      >
        <div class="d-flex">
          <div class="toast-body">
            {{ message }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { Toast } from 'bootstrap';

const studentId = ref(''); // Lấy từ localStorage khi tích hợp authentication
const classes = ref([]);
const selectedClassId = ref('');
const teachers = ref([]);
const classrooms = ref([]);
const activeTab = ref('teachers');
const message = ref('');
const messageType = ref('info');
const feedbackAvailability = ref(null);
const loadingTeachers = ref(false);
const loadingClassrooms = ref(false);
const toast = ref(null);

const feedbackContent = ref({
  teachers: {},
  classrooms: {}
});

// Computed property để kiểm tra nếu có thể đánh giá
const canFeedback = computed(() => {
  return feedbackAvailability.value && feedbackAvailability.value.can_feedback;
});

// Computed property để hiển thị trạng thái
const statusMessage = computed(() => {
  if (!feedbackAvailability.value) return 'Chọn lớp';
  
  switch (feedbackAvailability.value.status) {
    case 'available': return 'Đang mở đánh giá';
    case 'upcoming': return 'Sắp mở đánh giá';
    default: return 'Đã đóng đánh giá';
  }
});

onMounted(async () => {
  // Lấy student_id từ localStorage
  studentId.value = localStorage.getItem('student_id');
  
  // Nếu không có student_id, hiển thị thông báo lỗi
  if (!studentId.value) {
    showMessage('Không tìm thấy thông tin sinh viên, vui lòng đăng nhập lại', 'danger');
    return;
  }
  
  await loadClasses();
});

const loadClasses = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/api/class_students/student/${studentId.value}/classes`);
    if (response.data && response.data.items) {
      // API returns paginated data
      classes.value = response.data.items;
    } else {
      // API returns direct array (backward compatibility)
      classes.value = response.data;
    }
  } catch (error) {
    showMessage('Không thể tải danh sách lớp học', 'danger');
  }
};

const loadData = async () => {
  if (!selectedClassId.value) return;
  
  try {
    // Kiểm tra khả năng đánh giá
    const availabilityResponse = await axios.get(
      `http://localhost:5000/api/feedback_availability/${selectedClassId.value}`
    );
    feedbackAvailability.value = availabilityResponse.data;
    
    // Tải danh sách giảng viên
    loadingTeachers.value = true;
    try {
      const teacherResponse = await axios.get(
        `http://localhost:5000/api/class_teachers/student/${studentId.value}/classes/${selectedClassId.value}/teachers`
      );
      teachers.value = teacherResponse.data;
    } finally {
      loadingTeachers.value = false;
    }
    
    // Tải danh sách phòng học
    loadingClassrooms.value = true;
    try {
      const classroomResponse = await axios.get(
        `http://localhost:5000/api/classroom_feedbacks/student/${studentId.value}/classes/${selectedClassId.value}/classrooms`
      );
      classrooms.value = classroomResponse.data;
    } finally {
      loadingClassrooms.value = false;
    }
    
  } catch (error) {
    showMessage('Không thể tải dữ liệu', 'danger');
  }
};

const submitTeacherFeedback = async (teacherId) => {
  if (!canFeedback.value) {
    showMessage(getSubmitErrorMessage(), 'warning');
    return;
  }
  
  const content = feedbackContent.value.teachers[teacherId];
  
  if (!content || content.trim() === '') {
    showMessage('Vui lòng nhập nội dung đánh giá', 'warning');
    return;
  }
  
  try {
    await axios.post('http://localhost:5000/api/teacher_feedbacks', {
      content,
      student_id: studentId.value,
      class_id: selectedClassId.value,
      teacher_id: teacherId
    });
    
    showMessage('Đánh giá giảng viên đã được gửi thành công', 'success');
    feedbackContent.value.teachers[teacherId] = '';
    
    // Tải lại danh sách
    loadData();
    
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      showMessage(error.response.data.message, 'danger');
    } else {
      showMessage('Có lỗi xảy ra khi gửi đánh giá', 'danger');
    }
  }
};

const submitClassroomFeedback = async (classroomId) => {
  if (!canFeedback.value) {
    showMessage(getSubmitErrorMessage(), 'warning');
    return;
  }
  
  const content = feedbackContent.value.classrooms[classroomId];
  
  if (!content || content.trim() === '') {
    showMessage('Vui lòng nhập nội dung đánh giá', 'warning');
    return;
  }
  
  try {
    await axios.post('http://localhost:5000/api/classroom_feedbacks', {
      content,
      student_id: studentId.value,
      class_id: selectedClassId.value,
      classroom_id: classroomId
    });
    
    showMessage('Đánh giá phòng học đã được gửi thành công', 'success');
    feedbackContent.value.classrooms[classroomId] = '';
    
    // Tải lại danh sách
    loadData();
    
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      showMessage(error.response.data.message, 'danger');
    } else {
      showMessage('Có lỗi xảy ra khi gửi đánh giá', 'danger');
    }
  }
};

const getStatusClass = (status) => {
  switch (status) {
    case 'available': return 'alert-success';
    case 'upcoming': return 'alert-info';
    default: return 'alert-secondary';
  }
};

const getStatusIcon = (status) => {
  switch (status) {
    case 'available': return 'bi-check-circle-fill';
    case 'upcoming': return 'bi-hourglass-split';
    default: return 'bi-calendar-x-fill';
  }
};

const getStatusTitle = (status) => {
  switch (status) {
    case 'available': return 'Đang trong thời gian đánh giá';
    case 'upcoming': return 'Sắp đến thời gian đánh giá';
    default: return 'Đã kết thúc thời gian đánh giá';
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric' 
  });
};

const getButtonText = () => {
  if (!feedbackAvailability.value) return 'Gửi đánh giá';
  
  switch (feedbackAvailability.value.status) {
    case 'available': return 'Gửi đánh giá';
    case 'upcoming': return 'Chưa đến thời gian đánh giá';
    default: return 'Đã hết thời gian đánh giá';
  }
};

const getSubmitErrorMessage = () => {
  if (!feedbackAvailability.value) return 'Không thể đánh giá';
  
  switch (feedbackAvailability.value.status) {
    case 'upcoming': return 'Chưa đến thời gian đánh giá';
    case 'expired': return 'Đã quá thời gian đánh giá';
    default: return 'Không thể đánh giá';
  }
};

const getNoTeacherMessage = () => {
  if (!canFeedback.value && teachers.value.length === 0) {
    return 'Bạn đã đánh giá tất cả giảng viên hoặc chưa đến thời gian đánh giá';
  }
  return 'Bạn đã đánh giá tất cả giảng viên trong lớp học này';
};

const getNoClassroomMessage = () => {
  if (!canFeedback.value && classrooms.value.length === 0) {
    return 'Bạn đã đánh giá tất cả phòng học hoặc chưa đến thời gian đánh giá';
  }
  return 'Bạn đã đánh giá tất cả phòng học trong lớp học này';
};

const getInitials = (firstName, lastName) => {
  return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase();
};

const showMessage = (msg, type = 'info') => {
  message.value = msg;
  messageType.value = type;
  
  // Sử dụng Bootstrap Toast
  if (toast.value) {
    const bsToast = new Toast(toast.value);
    bsToast.show();
  }
};
</script>

<style scoped>
.avatar-placeholder {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #6c757d;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
}

.room-placeholder {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.hover-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

/* Responsive */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: start !important;
  }
  
  .card-header .badge {
    margin-top: 8px;
  }
}
</style>
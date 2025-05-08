<template>
  <div class="container mt-4">
    <h2 class="mb-4">Chấm điểm bài thi</h2>
    
    <!-- Loading spinner -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Đang tải danh sách đợt thi...</p>
    </div>
    
    <!-- Exams list -->
    <div v-else-if="exams.length > 0" class="row">
      <div v-for="exam in exams" :key="exam.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100 shadow-sm">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">{{ exam.title }}</h5>
            <span class="badge bg-primary">{{ getClassCode(exam.class_id) }}</span>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <p class="mb-1"><strong>Ngày thi:</strong> {{ formatDate(exam.exam_date) }}</p>
              <p class="mb-1"><strong>Thời gian:</strong> {{ exam.exam_start_time }} - {{ exam.exam_end_time }}</p>
              <p class="mb-0"><strong>Trạng thái:</strong> 
                <span :class="getStatusClass(exam)">{{ getStatusText(exam) }}</span>
              </p>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <span v-if="!hasError(exam.id)" class="badge bg-info me-1">{{ getSubmissionCount(exam) }} bài nộp</span>
                <span v-else class="badge bg-warning text-dark">
                  <i class="bi bi-exclamation-triangle me-1"></i>Không thể tải dữ liệu
                </span>
              </div>
              <router-link :to="`/teacher/exams/${exam.id}/grading`" class="btn btn-primary btn-sm">
                <i class="bi bi-check-square me-1"></i>Chấm điểm
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty state -->
    <div v-else class="text-center my-5">
      <i class="bi bi-clipboard-x fs-1 text-muted"></i>
      <p class="mt-2">Không có đợt thi nào cần chấm điểm.</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';

export default {
  setup() {
    const exams = ref([]);
    const loading = ref(true);
    const teacherClasses = ref([]);
    const submissionStats = ref({});
    
    const fetchExams = async () => {
      try {
        loading.value = true;
        const response = await api.get('/exams');
        exams.value = response.data || [];
        
        // Fetch submission stats for each exam
        for (const exam of exams.value) {
          try {
            const statsResponse = await api.get(`/teacher/exams/${exam.id}/answers`);
            if (statsResponse.data.success) {
              submissionStats.value[exam.id] = {
                total: statsResponse.data.student_answers.length,
                graded: statsResponse.data.student_answers.filter(s => 
                  s.answers.every(a => a.is_correct !== null || a.score !== null)
                ).length
              };
            } else {
              // API returned success=false
              submissionStats.value[exam.id] = { total: 0, graded: 0, error: true };
              console.warn(`API error for exam ${exam.id}: ${statsResponse.data.message}`);
            }
          } catch (error) {
            // Handle network errors or server errors (500)
            console.error(`Error fetching stats for exam ${exam.id}:`, error);
            submissionStats.value[exam.id] = { total: 0, graded: 0, error: true };
          }
        }
      } catch (error) {
        console.error('Error fetching exams:', error);
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
      }
    };
    
    const getClassCode = (classId) => {
      const cls = teacherClasses.value.find(c => c.id === classId);
      return cls ? cls.code : 'N/A';
    };
    
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString('vi-VN');
    };
    
    const getStatusText = (exam) => {
      const now = new Date();
      const examDate = new Date(exam.exam_date);
      examDate.setHours(
        parseInt(exam.exam_end_time.split(':')[0]),
        parseInt(exam.exam_end_time.split(':')[1])
      );
      
      if (now < examDate) {
        return 'Đang diễn ra';
      } else {
        return 'Đã kết thúc';
      }
    };
    
    const getStatusClass = (exam) => {
      const status = getStatusText(exam);
      return {
        'text-warning fw-bold': status === 'Đang diễn ra',
        'text-success fw-bold': status === 'Đã kết thúc'
      };
    };
    
    const getSubmissionCount = (exam) => {
      return submissionStats.value[exam.id]?.total || 0;
    };
    
    const getGradedCount = (exam) => {
      return submissionStats.value[exam.id]?.graded || 0;
    };
    
    const hasError = (examId) => {
      return submissionStats.value[examId]?.error === true;
    };
    
    onMounted(async () => {
      await fetchTeacherClasses();
      await fetchExams();
    });
    
    return {
      exams,
      loading,
      getClassCode,
      formatDate,
      getStatusText,
      getStatusClass,
      getSubmissionCount,
      getGradedCount,
      hasError
    };
  }
};
</script>

<style scoped>
.card {
  transition: transform 0.3s ease;
}
.card:hover {
  transform: translateY(-5px);
}
.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  padding: 0.75rem 1.25rem;
}
</style> 
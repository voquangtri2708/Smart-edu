<template>
  <div class="exam-grading container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Chấm điểm bài thi</h2>
      <button class="btn btn-secondary" @click="goBack">
        <i class="bi bi-arrow-left"></i> Quay lại
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Đang tải dữ liệu bài thi...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Exam content -->
    <template v-else>
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">{{ exam.title }}</h4>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <p><strong>Lớp:</strong> {{ classInfo.code }}</p>
              <p><strong>Ngày thi:</strong> {{ formatDate(exam.exam_date) }}</p>
              <p><strong>Thời gian:</strong> {{ exam.exam_start_time }} - {{ exam.exam_end_time }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Thời lượng:</strong> {{ exam.duration_minutes }} phút</p>
              <p v-if="examDetail.grade_type"><strong>Loại điểm:</strong> {{ examDetail.grade_type.name }}</p>
              <p v-if="examDetail.grade_type"><strong>Hệ số:</strong> {{ examDetail.grade_type ? (examDetail.grade_type.weight * 100).toFixed(0) + '%' : 'N/A' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Student submissions -->
      <div class="card">
        <div class="card-header">
          <h5>Bài làm của sinh viên ({{ studentAnswers.length }})</h5>
        </div>
        <div class="card-body">
          <!-- Empty state -->
          <div v-if="studentAnswers.length === 0" class="text-center py-4">
            <i class="bi bi-clipboard-x fs-2 text-muted"></i>
            <p class="mt-2">Chưa có sinh viên nộp bài</p>
          </div>

          <!-- Student list -->
          <div v-else class="table-responsive">
            <table class="table table-bordered table-hover">
              <thead class="table-light">
                <tr>
                  <th width="5%">#</th>
                  <th width="15%">Mã sinh viên</th>
                  <th width="25%">Họ và tên</th>
                  <th width="15%">Điểm số</th>
                  <th width="15%">Điểm trắc nghiệm</th>
                  <th width="15%">Thao tác</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(student, index) in studentAnswers" :key="student.student_id">
                  <td>{{ index + 1 }}</td>
                  <td>{{ student.student_code }}</td>
                  <td>{{ student.student_name }}</td>
                  <td>
                    <span v-if="hasGrade(student.student_id)" :class="getScoreClass(getStudentGrade(student.student_id))">
                      {{ getStudentGrade(student.student_id).toFixed(1) }}/10
                    </span>
                    <span v-else class="text-muted">Chưa chấm</span>
                  </td>
                  <td>
                    <span v-if="student.total_score !== null" :class="getScoreClass(student.total_score)">
                      {{ student.total_score.toFixed(1) }}
                    </span>
                    <span v-else class="text-muted">N/A</span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-info me-1" @click="viewStudentAnswers(student.student_id)">
                      <i class="bi bi-eye"></i> Xem chi tiết
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Toast notification -->
      <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div id="toast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
          <div class="toast-header" :class="{'text-white': true, 'bg-success': messageType === 'success', 'bg-danger': messageType === 'error'}">
            <strong class="me-auto">{{ messageType === 'success' ? 'Thành công' : 'Lỗi' }}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
          </div>
          <div class="toast-body">
            {{ message }}
          </div>
        </div>
      </div>

      <!-- Student Answers Modal -->
      <div class="modal fade" id="studentAnswersModal" tabindex="-1" aria-labelledby="studentAnswersModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="studentAnswersModalLabel" v-if="currentStudentId">
                Bài làm của sinh viên: {{ getStudentName(currentStudentId) }}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" v-if="currentStudentAnswers">
              <div class="table-responsive">
                <table class="table table-bordered table-hover">
                  <thead class="table-light">
                    <tr>
                      <th width="5%">#</th>
                      <th width="40%">Câu hỏi</th>
                      <th width="15%">Loại</th>
                      <th width="25%">Câu trả lời</th>
                      <th width="15%">Trạng thái</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(answer, index) in currentStudentAnswers.answers" :key="answer.id">
                      <td>{{ index + 1 }}</td>
                      <td>{{ getQuestionText(answer.question_id) }}</td>
                      <td>{{ getQuestionType(answer.question_id) }}</td>
                      <td>
                        <!-- Show actual answer text for multiple choice and true/false -->
                        <template v-if="['Trắc nghiệm', 'Đúng/Sai'].includes(getQuestionType(answer.question_id))">
                          {{ getActualAnswerText(answer.answer_text, answer.question_id) }}
                        </template>
                        <template v-else>
                          {{ answer.answer_text }}
                        </template>
                      </td>
                      <td>
                        <span 
                          :class="{
                            'badge bg-success': answer.is_correct === true,
                            'badge bg-danger': answer.is_correct === false,
                            'badge bg-secondary': answer.is_correct === null
                          }"
                        >
                          {{ getAnswerStatus(answer) }}
                        </span>
                        <span v-if="answer.score !== null" class="ms-2">
                          ({{ answer.score }} điểm)
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!-- Add score input in modal -->
              <div class="mt-3 border-top pt-3">
                <div class="row align-items-center">
                  <div class="col-md-6">
                    <p class="mb-1">Điểm trắc nghiệm: 
                      <span v-if="currentStudentAnswers.total_score !== null" 
                            :class="getScoreClass(currentStudentAnswers.total_score)">
                        {{ currentStudentAnswers.total_score.toFixed(1) }}
                      </span>
                      <span v-else class="text-muted">N/A</span>
                    </p>
                  </div>
                  <div class="col-md-6">
                    <div class="input-group">
                      <span class="input-group-text">Điểm số</span>
                      <input 
                        type="number" 
                        class="form-control" 
                        v-model="studentGrades[currentStudentId]" 
                        min="0" 
                        max="10" 
                        step="0.1"
                        aria-label="Điểm số"
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
              <button type="button" class="btn btn-primary" @click="saveGradeFromModal">Lưu điểm</button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Modal, Toast } from 'bootstrap';
import api from '@/utils/api';

export default {
  name: 'TeacherExamGradingView',
  props: {
    examId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    const examId = computed(() => props.examId || route.params.examId);

    // Data
    const loading = ref(true);
    const error = ref(null);
    const exam = ref({});
    const examDetail = ref({});
    const classInfo = ref({});
    const questions = ref([]);
    const studentAnswers = ref([]);
    const gradeTypes = ref([]);
    const toast = ref(null);
    const message = ref('');
    const messageType = ref('');
    const studentGrades = ref({});
    const studentExistingGrades = ref({});
    const answersModal = ref(null);
    const currentStudentId = ref(null);
    const currentStudentAnswers = ref(null);
    
    // Methods
    const goBack = () => {
      router.push('/teacher/exams');
    };
    
    const fetchExamData = async () => {
      try {
        loading.value = true;
        const response = await api.get(`/teacher/exams/${examId.value}/answers`);
        console.log('Exam data response:', response.data);
        if (response.data.success) {
          // Get basic exam info from the answer response
          exam.value = response.data.exam;
          questions.value = response.data.questions;
          studentAnswers.value = response.data.student_answers;
          
          // Initialize student grades
          studentAnswers.value.forEach(student => {
            studentGrades.value[student.student_id] = student.total_score || 0;
          });
          
          // Fetch detailed exam info and merge it with exam.value
          await fetchFullExamDetails();
          
          // Fetch grade types
          await fetchGradeTypes();
          
          // Get existing grades
          await fetchExistingGrades();
          
          // Debug output
          console.log('Final exam object:', exam.value);
        } else {
          error.value = response.data.message || 'Failed to load exam data';
        }
      } catch (err) {
        console.error('Error fetching exam data:', err);
        error.value = err.response?.data?.message || 'Không thể tải dữ liệu bài thi. Vui lòng thử lại sau.';
        
        if (err.response?.data?.error) {
          error.value += ` (Error: ${err.response.data.error})`;
        }
      } finally {
        loading.value = false;
      }
    };
    
    // New combined function to get full exam details
    const fetchFullExamDetails = async () => {
      try {
        // Get detailed exam info
        const response = await api.get(`/exams/${examId.value}`);
        console.log('Exam details response:', response.data);
        examDetail.value = response.data;
        
        // Copy missing fields from examDetail to exam
        if (examDetail.value) {
          // Update exam with detailed info
          exam.value = {
            ...exam.value,
            exam_date: examDetail.value.exam_date,
            duration_minutes: examDetail.value.duration_minutes,
            exam_start_time: examDetail.value.exam_start_time,
            exam_end_time: examDetail.value.exam_end_time,
            // Also add the alternative naming used in student view
            start_time: examDetail.value.exam_start_time,
            end_time: examDetail.value.exam_end_time
          };
        }
        
        // Get class info
        if (examDetail.value?.class_id) {
          const classResponse = await api.get(`/classes/${examDetail.value.class_id}`);
          classInfo.value = classResponse.data;
        }
      } catch (err) {
        console.error('Error fetching detailed exam info:', err);
      }
    };
    
    const fetchGradeTypes = async () => {
      try {
        const response = await api.get('/grade_types');
        gradeTypes.value = response.data;
      } catch (err) {
        console.error('Error fetching grade types:', err);
      }
    };
    
    const fetchExistingGrades = async () => {
      try {
        // Get the class_id from the exam
        const examDetailResponse = await api.get(`/exams/${examId.value}`);
        if (examDetailResponse.data) {
          const classId = examDetailResponse.data.class_id;
          
          // For each student, check if they have an existing grade for this exam
          for (const student of studentAnswers.value) {
            const response = await api.get(`/classes/${classId}/students/${student.student_id}/grades`);
            const grades = response.data;
            
            // Find a grade that matches this exam
            const examGrade = grades.find(g => g.exam_id === parseInt(examId.value));
            if (examGrade) {
              studentExistingGrades.value[student.student_id] = examGrade;
              studentGrades.value[student.student_id] = examGrade.score;
            }
          }
        }
      } catch (err) {
        console.error('Error fetching existing grades:', err);
      }
    };
    
    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString('vi-VN');
    };
    
    const hasGrade = (studentId) => {
      return studentId in studentExistingGrades.value;
    };
    
    const getStudentGrade = (studentId) => {
      return studentExistingGrades.value[studentId]?.score || 0;
    };
    
    const getScoreClass = (score) => {
      if (score >= 8) return 'text-success fw-bold';
      if (score >= 5) return 'text-primary';
      return 'text-danger';
    };
    
    const isValidScore = (score) => {
      return !isNaN(score) && score >= 0 && score <= 10;
    };
    
    const saveStudentGrade = async (studentId) => {
      // Check if the exam has a grade_type_id
      if (!examDetail.value.grade_type_id) {
        showMessage('Bài thi này chưa có loại điểm. Vui lòng cập nhật thông tin bài thi trước.', 'error');
        return;
      }
      
      if (!isValidScore(studentGrades.value[studentId])) {
        showMessage('Điểm số phải từ 0-10', 'error');
        return;
      }
      
      try {
        if (!examDetail.value) {
          showMessage('Không tìm thấy thông tin bài thi', 'error');
          return;
        }
        
        const classId = examDetail.value.class_id;
        
        // Check if student already has a grade for this exam
        if (studentId in studentExistingGrades.value) {
          // Update existing grade
          const gradeId = studentExistingGrades.value[studentId].id;
          await api.put(`/grades/${gradeId}`, {
            score: parseFloat(studentGrades.value[studentId])
          });
        } else {
          // Create new grade
          await api.post('/grades', {
            student_id: studentId,
            class_id: classId,
            grade_type_id: examDetail.value.grade_type_id,
            exam_id: parseInt(examId.value),
            score: parseFloat(studentGrades.value[studentId])
          });
          
          // Update local record of existing grades
          await fetchExistingGrades();
        }
        
        showMessage('Lưu điểm thành công', 'success');
      } catch (err) {
        console.error('Error saving grade:', err);
        showMessage(err.response?.data?.message || 'Lỗi khi lưu điểm', 'error');
      }
    };
    
    const viewStudentAnswers = (studentId) => {
      currentStudentId.value = studentId;
      currentStudentAnswers.value = studentAnswers.value.find(s => s.student_id === studentId);
      
      if (!answersModal.value) {
        answersModal.value = new Modal(document.getElementById('studentAnswersModal'));
      }
      
      answersModal.value.show();
    };
    
    const getStudentName = (studentId) => {
      const student = studentAnswers.value.find(s => s.student_id === studentId);
      return student ? student.student_name : '';
    };
    
    const getQuestionText = (questionId) => {
      const question = questions.value.find(q => q.id === questionId);
      return question ? question.question_text : '';
    };
    
    const getQuestionType = (questionId) => {
      const question = questions.value.find(q => q.id === questionId);
      if (!question) return '';
      
      switch (question.question_type) {
        case 'MULTIPLE_CHOICE': return 'Trắc nghiệm';
        case 'TRUE_FALSE': return 'Đúng/Sai';
        case 'ESSAY': return 'Tự luận';
        case 'SHORT_ANSWER': return 'Trả lời ngắn';
        default: return question.question_type;
      }
    };
    
    const getCorrectAnswer = (questionId) => {
      const question = questions.value.find(q => q.id === questionId);
      return question ? question.correct_answer : '';
    };
    
    const getActualAnswerText = (answerId, questionId) => {
      // Find the question
      const question = questions.value.find(q => q.id === questionId);
      if (!question) return answerId;
      
      // For multiple choice and true/false questions, we need to fetch all available answers
      // to match the ID with the text
      
      // First check in correct_answers (these come from the API)
      if (question.correct_answers) {
        for (const answer of question.correct_answers) {
          if (answer.id == answerId) {
            return answer.text;
          }
        }
      }
      
      // Then check in answers array (also from API but structured differently)
      if (question.answers) {
        for (const answer of question.answers) {
          if (answer.id == answerId) {
            return answer.answer_text;
          }
        }
      }
      
      // If we still couldn't find it, we'll make an API call to fetch the answer
      const fetchAnswerText = async () => {
        try {
          // Since we're in a method not an async function, we need to handle 
          // the promise resolution separately
          const response = await api.get(`/questions/${questionId}`);
          
          if (response.data && response.data.answers) {
            for (const answer of response.data.answers) {
              if (answer.id == answerId) {
                // We found the answer, now update the display
                // We're mutating the question object to cache this for future use
                if (!question.answers) question.answers = [];
                question.answers.push(answer);
                return answer.answer_text;
              }
            }
          }
        } catch (error) {
          console.error('Error fetching answer details:', error);
        }
        return answerId; // Default fallback
      };
      
      // Trigger the fetch but return the ID for now (it will update when data arrives)
      fetchAnswerText();
      
      // Return the ID as fallback while we wait for the API call
      return answerId;
    };
    
    const getAnswerStatus = (answer) => {
      if (answer.is_correct === true) return 'Đúng';
      if (answer.is_correct === false) return 'Sai';
      return 'Chưa chấm';
    };
    
    const saveGradeFromModal = async () => {
      if (currentStudentId.value) {
        await saveStudentGrade(currentStudentId.value);
        answersModal.value.hide();
      }
    };
    
    const showMessage = (msg, type) => {
      message.value = msg;
      messageType.value = type;
      
      if (!toast.value) {
        toast.value = new Toast(document.getElementById('toast'));
      }
      
      toast.value.show();
    };
    
    onMounted(async () => {
      await fetchExamData();
    });
    
    return {
      loading,
      error,
      exam,
      examDetail,
      classInfo,
      questions,
      studentAnswers,
      gradeTypes,
      studentGrades,
      message,
      messageType,
      currentStudentId,
      currentStudentAnswers,
      goBack,
      formatDate,
      hasGrade,
      getStudentGrade,
      getScoreClass,
      isValidScore,
      saveStudentGrade,
      viewStudentAnswers,
      getStudentName,
      getQuestionText,
      getQuestionType,
      getCorrectAnswer,
      getAnswerStatus,
      getActualAnswerText,
      saveGradeFromModal
    };
  }
};
</script>

<style scoped>
.exam-grading {
  max-width: 1200px;
  margin: 0 auto;
}

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
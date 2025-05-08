<template>
  <div class="grade-entry container py-4">
    <div class="card shadow-sm mb-4">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Nhập điểm sinh viên</h4>
      </div>
      <div class="card-body">
        <!-- Loading indicator -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Đang tải...</span>
          </div>
          <p class="mt-2">Đang tải dữ liệu...</p>
        </div>
        
        <!-- Content when loaded -->
        <div v-else>
          <!-- Step 1: Chọn lớp học -->
          <div class="mb-4">
            <h5 class="mb-3">1. Chọn lớp học</h5>
            <div class="row">
              <div class="col-md-6">
                <select class="form-select" v-model="selectedClassId" @change="onClassChange">
                  <option value="">-- Chọn lớp học --</option>
                  <option v-for="class_ in classes" :key="class_.id" :value="class_.id">
                    {{ class_.subject_code }} - {{ class_.subject_name }} ({{ class_.code }})
                  </option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Step 2: Chọn loại điểm (hiển thị khi đã chọn lớp) -->
          <div v-if="selectedClassId" class="mb-4">
            <h5 class="mb-3">2. Chọn loại điểm</h5>
            <div class="row">
              <div class="col-md-6">
                <select class="form-select" v-model="selectedGradeTypeId" @change="onGradeTypeChange">
                  <option value="">-- Chọn loại điểm --</option>
                  <option v-for="gradeType in gradeTypes" :key="gradeType.id" :value="gradeType.id">
                    {{ gradeType.name }} ({{ gradeType.weight * 100 }}%)
                  </option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Step 3: Danh sách sinh viên để nhập điểm (hiển thị khi đã chọn loại điểm) -->
          <div v-if="selectedGradeTypeId && students.length > 0" class="mb-4">
            <h5 class="mb-3">3. Nhập điểm cho sinh viên</h5>
            
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
                    placeholder="Tìm kiếm sinh viên..." 
                    v-model="searchQuery"
                    @input="filterStudents"
                  >
                </div>
              </div>
              <div class="col-md-6 text-end">
                <button class="btn btn-success" @click="saveAllGrades" :disabled="processing">
                  <i class="bi bi-save me-1"></i>Lưu tất cả điểm
                </button>
              </div>
            </div>
            
            <!-- Students table -->
            <div class="table-responsive">
              <table class="table table-striped table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th scope="col" width="5%">#</th>
                    <th scope="col" width="15%">Mã sinh viên</th>
                    <th scope="col" width="30%">Họ và tên</th>
                    <th scope="col" width="20%">Điểm số</th>
                    <th scope="col" width="30%">Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in filteredStudents" :key="student.id">
                    <td>{{ index + 1 }}</td>
                    <td>{{ student.id }}</td>
                    <td>{{ student.last_name }} {{ student.first_name }}</td>
                    <td>
                      <div class="input-group">
                        <input 
                          type="number" 
                          class="form-control" 
                          v-model="studentGrades[student.id]" 
                          min="0" 
                          max="10" 
                          step="0.1" 
                          :disabled="processing"
                        >
                        <span class="input-group-text">/10</span>
                      </div>
                    </td>
                    <td>
                      <button 
                        class="btn btn-primary btn-sm me-2" 
                        @click="saveGrade(student.id)"
                        :disabled="processing || !isValidScore(studentGrades[student.id])"
                      >
                        <span v-if="processing && processingStudentId === student.id" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                        <i v-else class="bi bi-save me-1"></i>
                        Lưu
                      </button>
                      <span v-if="!isValidScore(studentGrades[student.id])" class="text-danger">
                        <small>Điểm phải từ 0-10</small>
                      </span>
                      <span v-else-if="savedStudents[student.id]" class="text-success">
                        <i class="bi bi-check-circle me-1"></i>
                        <small>Đã lưu</small>
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- No students found -->
          <div v-else-if="selectedGradeTypeId && students.length === 0" class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>
            Không có sinh viên nào trong lớp học này.
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast Notification -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div id="notification" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header" :class="{'bg-success text-white': messageType === 'success', 'bg-danger text-white': messageType === 'danger', 'bg-warning': messageType === 'warning', 'bg-info text-white': messageType === 'info'}">
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
import { ref, onMounted, computed } from 'vue';
import api from '@/utils/api';
import { Toast } from 'bootstrap';

export default {
  name: 'TeacherGradeEntry',
  setup() {
    // State
    const loading = ref(true);
    const classes = ref([]);
    const students = ref([]);
    const gradeTypes = ref([]);
    const selectedClassId = ref('');
    const selectedGradeTypeId = ref('');
    const studentGrades = ref({});
    const processing = ref(false);
    const processingStudentId = ref(null);
    const savedStudents = ref({});
    const searchQuery = ref('');
    const filteredStudents = ref([]);
    
    // Toast notification
    const message = ref('');
    const messageType = ref('success');
    const toastTitle = ref('Thông báo');
    let toastInstance = null;
    
    // Fetch classes taught by the teacher
    const fetchClasses = async () => {
      try {
        loading.value = true;
        // Tạo đường dẫn API đúng
        const teacherId = localStorage.getItem('teacher_id');
        const response = await api.get(`/teacher/classes`);
        
        if (Array.isArray(response.data)) {
          classes.value = response.data;
        } else {
          classes.value = [];
          showMessage('Có lỗi khi tải danh sách lớp học', 'danger', 'Lỗi');
        }
      } catch (error) {
        console.error('Error fetching classes:', error);
        showMessage('Không thể tải danh sách lớp học', 'danger', 'Lỗi');
      } finally {
        loading.value = false;
      }
    };
    
    // Fetch students when a class is selected
    const fetchStudents = async () => {
      if (!selectedClassId.value) return;
      
      try {
        loading.value = true;
        const response = await api.get(`/class_students/class/${selectedClassId.value}/students`);
        
        if (response.data && response.data.items) {
          students.value = response.data.items;
          filteredStudents.value = [...students.value];
          
          // Reset student grades
          studentGrades.value = {};
          savedStudents.value = {};
          
          // Khởi tạo mảng điểm trống cho mỗi sinh viên
          students.value.forEach(student => {
            studentGrades.value[student.id] = '';
          });
          
          // Nếu đã chọn loại điểm, tải điểm hiện có
          if (selectedGradeTypeId.value) {
            fetchExistingGrades();
          }
        } else {
          students.value = [];
          filteredStudents.value = [];
          showMessage('Không tìm thấy sinh viên trong lớp học này', 'info', 'Thông tin');
        }
      } catch (error) {
        console.error('Error fetching students:', error);
        showMessage('Không thể tải danh sách sinh viên', 'danger', 'Lỗi');
      } finally {
        loading.value = false;
      }
    };
    
    // Fetch grade types when a class is selected
    const fetchGradeTypes = async () => {
      if (!selectedClassId.value) return;
      
      try {
        loading.value = true;
        const response = await api.get(`/grade_types`);
        
        if (Array.isArray(response.data)) {
          gradeTypes.value = response.data;
        } else {
          gradeTypes.value = [];
          showMessage('Không tìm thấy loại điểm nào', 'info', 'Thông tin');
        }
      } catch (error) {
        console.error('Error fetching grade types:', error);
        showMessage('Không thể tải danh sách loại điểm', 'danger', 'Lỗi');
      } finally {
        loading.value = false;
      }
    };
    
    // Fetch existing grades for the selected class and grade type
    const fetchExistingGrades = async () => {
      if (!selectedClassId.value || !selectedGradeTypeId.value) return;
      
      try {
        loading.value = true;
        const response = await api.get(`/classes/${selectedClassId.value}/grades`);
        
        if (Array.isArray(response.data)) {
          // Filter grades by the selected grade type
          const relevantGrades = response.data.filter(grade => 
            grade.grade_type_id === parseInt(selectedGradeTypeId.value)
          );
          
          // Update student grades with existing values
          relevantGrades.forEach(grade => {
            studentGrades.value[grade.student_id] = grade.score;
            // Mark these students as already having grades saved
            savedStudents.value[grade.student_id] = true;
          });
        }
      } catch (error) {
        console.error('Error fetching existing grades:', error);
        showMessage('Không thể tải điểm hiện có', 'warning', 'Cảnh báo');
      } finally {
        loading.value = false;
      }
    };
    
    // Handle class selection change
    const onClassChange = () => {
      selectedGradeTypeId.value = '';
      students.value = [];
      filteredStudents.value = [];
      studentGrades.value = {};
      savedStudents.value = {};
      
      if (selectedClassId.value) {
        fetchGradeTypes();
      }
    };
    
    // Handle grade type selection change
    const onGradeTypeChange = () => {
      if (selectedGradeTypeId.value && selectedClassId.value) {
        fetchStudents();
      }
    };
    
    // Filter students based on search query
    const filterStudents = () => {
      if (!searchQuery.value.trim()) {
        filteredStudents.value = [...students.value];
        return;
      }
      
      const query = searchQuery.value.toLowerCase();
      filteredStudents.value = students.value.filter(student => 
        student.id.toLowerCase().includes(query) ||
        student.first_name.toLowerCase().includes(query) ||
        student.last_name.toLowerCase().includes(query)
      );
    };
    
    // Check if a score is valid
    const isValidScore = (score) => {
      if (score === '' || score === null || score === undefined) return false;
      
      const numScore = parseFloat(score);
      return !isNaN(numScore) && numScore >= 0 && numScore <= 10;
    };
    
    // Save grade for a single student
    const saveGrade = async (studentId) => {
      if (!isValidScore(studentGrades.value[studentId])) {
        showMessage('Điểm phải từ 0 đến 10', 'warning', 'Cảnh báo');
        return;
      }
      
      processing.value = true;
      processingStudentId.value = studentId;
      
      try {
        // Check if student already has a grade for this grade type
        const response = await api.get(`/classes/${selectedClassId.value}/students/${studentId}/grades`);
        
        let existingGrade = null;
        if (Array.isArray(response.data)) {
          existingGrade = response.data.find(grade => 
            grade.grade_type_id === parseInt(selectedGradeTypeId.value)
          );
        }
        
        if (existingGrade) {
          // Update existing grade
          await api.put(`/grades/${existingGrade.id}`, {
            score: parseFloat(studentGrades.value[studentId])
          });
        } else {
          // Create new grade
          await api.post('/grades', {
            student_id: studentId,
            class_id: parseInt(selectedClassId.value),
            grade_type_id: parseInt(selectedGradeTypeId.value),
            score: parseFloat(studentGrades.value[studentId])
          });
        }
        
        // Mark the student as saved
        savedStudents.value[studentId] = true;
        
        showMessage('Đã lưu điểm thành công', 'success', 'Thành công');
      } catch (error) {
        console.error('Error saving grade:', error);
        
        let errorMessage = 'Không thể lưu điểm';
        if (error.response && error.response.data && error.response.data.message) {
          errorMessage = error.response.data.message;
        }
        
        showMessage(errorMessage, 'danger', 'Lỗi');
      } finally {
        processing.value = false;
        processingStudentId.value = null;
      }
    };
    
    // Save grades for all students
    const saveAllGrades = async () => {
      processing.value = true;
      
      try {
        // Filter students with valid grades
        const studentsWithGrades = filteredStudents.value.filter(student => 
          isValidScore(studentGrades.value[student.id])
        );
        
        if (studentsWithGrades.length === 0) {
          showMessage('Không có điểm hợp lệ để lưu', 'warning', 'Cảnh báo');
          return;
        }
        
        // Save grades for each student sequentially
        for (const student of studentsWithGrades) {
          processingStudentId.value = student.id;
          
          // Check if student already has a grade for this grade type
          const response = await api.get(`/classes/${selectedClassId.value}/students/${student.id}/grades`);
          
          let existingGrade = null;
          if (Array.isArray(response.data)) {
            existingGrade = response.data.find(grade => 
              grade.grade_type_id === parseInt(selectedGradeTypeId.value)
            );
          }
          
          if (existingGrade) {
            // Update existing grade
            await api.put(`/grades/${existingGrade.id}`, {
              score: parseFloat(studentGrades.value[student.id])
            });
          } else {
            // Create new grade
            await api.post('/grades', {
              student_id: student.id,
              class_id: parseInt(selectedClassId.value),
              grade_type_id: parseInt(selectedGradeTypeId.value),
              score: parseFloat(studentGrades.value[student.id])
            });
          }
          
          // Mark the student as saved
          savedStudents.value[student.id] = true;
        }
        
        showMessage('Đã lưu tất cả điểm thành công', 'success', 'Thành công');
      } catch (error) {
        console.error('Error saving all grades:', error);
        
        let errorMessage = 'Không thể lưu điểm';
        if (error.response && error.response.data && error.response.data.message) {
          errorMessage = error.response.data.message;
        }
        
        showMessage(errorMessage, 'danger', 'Lỗi');
      } finally {
        processing.value = false;
        processingStudentId.value = null;
      }
    };
    
    // Show toast message
    const showMessage = (text, type = 'success', title = 'Thông báo') => {
      message.value = text;
      messageType.value = type;
      toastTitle.value = title;
      
      // Initialize toast if not already
      if (!toastInstance) {
        const toastEl = document.getElementById('notification');
        if (toastEl) {
          toastInstance = new Toast(toastEl);
        }
      }
      
      // Show the toast
      if (toastInstance) {
        toastInstance.show();
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      fetchClasses();
      
      // Initialize toast
      const toastEl = document.getElementById('notification');
      if (toastEl) {
        toastInstance = new Toast(toastEl);
      }
    });
    
    return {
      loading,
      classes,
      students,
      filteredStudents,
      gradeTypes,
      selectedClassId,
      selectedGradeTypeId,
      studentGrades,
      processing,
      processingStudentId,
      savedStudents,
      searchQuery,
      message,
      messageType,
      toastTitle,
      
      onClassChange,
      onGradeTypeChange,
      filterStudents,
      isValidScore,
      saveGrade,
      saveAllGrades
    };
  }
};
</script>

<style scoped>
.table th, .table td {
  vertical-align: middle;
}

/* Animation for saved indicator */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.text-success {
  animation: fadeIn 0.5s ease-in-out;
}
</style>
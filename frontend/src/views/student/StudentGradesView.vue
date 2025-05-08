<template>
  <div class="student-grades-view">
    <div class="container mt-4">
      <div class="row mb-4">
        <div class="col-md-12">
          <h2 class="mb-3">Bảng điểm</h2>
          
          <!-- Lọc theo lớp học -->
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Lọc kết quả</h5>
            </div>
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-6">
                  <div class="mb-3 mb-md-0">
                    <select class="form-select" v-model="selectedClassId" @change="fetchGradesByClass">
                      <option value="">Tất cả các lớp</option>
                      <option v-for="class_ in classes" :key="class_.id" :value="class_.id">
                        {{ class_.code }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3 mb-md-0 d-flex align-items-end">
                    <button class="btn btn-primary" @click="fetchGrades">
                      <i class="bi bi-search me-1"></i>Lọc kết quả
                    </button>
                    <button class="btn btn-outline-secondary ms-2" @click="resetFilters">
                      <i class="bi bi-x-circle me-1"></i>Xóa lọc
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Loading indicator -->
          <div v-if="loading" class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Đang tải dữ liệu...</p>
          </div>
          
          <!-- Grades by class -->
          <div v-else-if="displayedGrades.length > 0">
            <div v-for="(classGrades, classId) in groupedGrades" :key="classId" class="card mb-4">
              <div class="card-header bg-light">
                <h5 class="mb-0">{{ getClassInfo(classId) }}</h5>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-striped table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th scope="col" width="5%">#</th>
                        <th scope="col" width="35%">Loại điểm</th>
                        <th scope="col" width="15%" class="text-center">Trọng số</th>
                        <th scope="col" width="15%" class="text-center">Điểm</th>
                        <th scope="col" width="30%" class="text-center">Tình trạng</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(grade, index) in classGrades" :key="grade.id">
                        <td>{{ index + 1 }}</td>
                        <td>{{ getGradeTypeName(grade.grade_type_id) }}</td>
                        <td class="text-center">{{ getGradeTypeWeight(grade.grade_type_id) }}%</td>
                        <td class="text-center">
                          <span :class="getScoreClass(grade.score)">
                            {{ grade.score }} / 10
                          </span>
                        </td>
                        <td class="text-center">
                          <span :class="getStatusClass(grade.score)">
                            {{ getStatusText(grade.score) }}
                          </span>
                        </td>
                      </tr>
                      <!-- Tổng điểm -->
                      <tr class="table-active fw-bold">
                        <td colspan="3" class="text-end">Tổng điểm trung bình:</td>
                        <td class="text-center">
                          <span :class="getScoreClass(getAverageScore(classGrades))">
                            {{ getAverageScore(classGrades).toFixed(2) }} / 10
                          </span>
                        </td>
                        <td class="text-center">
                          <span :class="getStatusClass(getAverageScore(classGrades))">
                            {{ getStatusText(getAverageScore(classGrades)) }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            
            <!-- Tổng kết học tập -->
            <div class="card">
              <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Tổng kết học tập</h5>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-4">
                    <div class="border rounded p-3 text-center h-100">
                      <h6 class="text-muted mb-2">Điểm trung bình tích lũy</h6>
                      <h3 :class="getScoreClass(getOverallAverage(displayedGrades))">{{ getOverallAverage(displayedGrades).toFixed(2) }}</h3>
                      <p class="mb-0 small">Thang điểm 10</p>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="border rounded p-3 text-center h-100">
                      <h6 class="text-muted mb-2">Tổng số lớp</h6>
                      <h3>{{ Object.keys(groupedGrades).length }}</h3>
                      <p class="mb-0 small">Đã hoàn thành</p>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="border rounded p-3 text-center h-100">
                      <h6 class="text-muted mb-2">Xếp loại</h6>
                      <h3 :class="getStatusClass(getOverallAverage(displayedGrades))">{{ getOverallClassification(getOverallAverage(displayedGrades)) }}</h3>
                      <p class="mb-0 small">Dựa trên điểm trung bình</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- No grades found -->
          <div v-else class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i> Không tìm thấy điểm nào. Hãy kiểm tra lại bộ lọc hoặc liên hệ với giáo viên.
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
import { ref, computed, onMounted } from 'vue';
import api from '@/utils/api';
import { Toast } from 'bootstrap';

export default {
  name: 'StudentGradesView',
  setup() {
    // State
    const loading = ref(true);
    const grades = ref([]);
    const classes = ref([]);
    const selectedClassId = ref('');
    const gradeTypes = ref([]);
    const message = ref('');
    const messageType = ref('success');
    const toastTitle = ref('Thông báo');
    let toastInstance = null;
    
    // Student ID
    const studentId = ref(localStorage.getItem('student_id'));
    
    // Computed
    const displayedGrades = computed(() => {
      // Nếu có lọc theo lớp
      if (selectedClassId.value) {
        return grades.value.filter(grade => 
          grade.class_id === parseInt(selectedClassId.value)
        );
      }
      
      // Trả về toàn bộ nếu không có lọc
      return grades.value;
    });
    
    // Group grades by class
    const groupedGrades = computed(() => {
      const grouped = {};
      
      displayedGrades.value.forEach(grade => {
        const classId = grade.class_id;
        
        if (!grouped[classId]) {
          grouped[classId] = [];
        }
        
        grouped[classId].push(grade);
      });
      
      return grouped;
    });
    
    // Fetch all grades for the student
    const fetchGrades = async () => {
      if (!studentId.value) {
        showMessage('Không tìm thấy thông tin sinh viên. Vui lòng đăng nhập lại.', 'danger');
        return;
      }
      
      loading.value = true;
      
      try {
        const response = await api.get(`/students/${studentId.value}/grades`);
        
        if (Array.isArray(response.data)) {
          grades.value = response.data;
        } else {
          grades.value = [];
          showMessage('Dữ liệu điểm không đúng định dạng', 'warning');
        }
      } catch (error) {
        console.error('Error fetching grades:', error);
        showMessage('Không thể tải dữ liệu điểm', 'danger');
        grades.value = [];
      }
      
      loading.value = false;
    };
    
    // Fetch grades by class
    const fetchGradesByClass = async () => {
      if (!selectedClassId.value || !studentId.value) {
        return fetchGrades();
      }
      
      loading.value = true;
      
      try {
        const response = await api.get(`/classes/${selectedClassId.value}/students/${studentId.value}/grades`);
        
        if (Array.isArray(response.data)) {
          grades.value = response.data;
        } else {
          grades.value = [];
          showMessage('Dữ liệu điểm không đúng định dạng', 'warning');
        }
      } catch (error) {
        console.error('Error fetching grades by class:', error);
        showMessage('Không thể tải dữ liệu điểm cho lớp này', 'danger');
        grades.value = [];
      }
      
      loading.value = false;
    };
    
    // Fetch classes that the student belongs to
    const fetchClasses = async () => {
      if (!studentId.value) return;
      
      try {
        const response = await api.get(`/class_students/student/${studentId.value}/classes`);
        
        if (response.data && response.data.items) {
          classes.value = response.data.items;
        } else if (Array.isArray(response.data)) {
          classes.value = response.data;
        } else {
          classes.value = [];
        }
      } catch (error) {
        console.error('Error fetching classes:', error);
        showMessage('Không thể tải danh sách lớp học', 'warning');
      }
    };
    
    // Fetch grade types
    const fetchGradeTypes = async () => {
      try {
        const response = await api.get('/grade_types');
        
        if (Array.isArray(response.data)) {
          gradeTypes.value = response.data;
        } else {
          gradeTypes.value = [];
        }
      } catch (error) {
        console.error('Error fetching grade types:', error);
      }
    };
    
    // Reset filters
    const resetFilters = () => {
      selectedClassId.value = '';
      fetchGrades();
    };
    
    // Get class info by ID
    const getClassInfo = (classId) => {
      const classObj = classes.value.find(c => c.id === parseInt(classId));
      if (classObj) {
        return `${classObj.code}`;
      }
      return `Lớp #${classId}`;
    };
    
    // Get grade type name by ID
    const getGradeTypeName = (gradeTypeId) => {
      const gradeType = gradeTypes.value.find(gt => gt.id === gradeTypeId);
      return gradeType ? gradeType.name : `Loại điểm #${gradeTypeId}`;
    };
    
    // Get grade type weight by ID
    const getGradeTypeWeight = (gradeTypeId) => {
      const gradeType = gradeTypes.value.find(gt => gt.id === gradeTypeId);
      return gradeType ? (gradeType.weight * 100).toFixed(0) : '0';
    };
    
    // Get score class based on score
    const getScoreClass = (score) => {
      if (score >= 8) return 'text-success fw-bold';
      if (score >= 6.5) return 'text-primary';
      if (score >= 5) return 'text-warning';
      return 'text-danger';
    };
    
    // Get status class based on score
    const getStatusClass = (score) => {
      if (score >= 8) return 'badge bg-success';
      if (score >= 6.5) return 'badge bg-primary';
      if (score >= 5) return 'badge bg-warning text-dark';
      return 'badge bg-danger';
    };
    
    // Get status text based on score
    const getStatusText = (score) => {
      if (score >= 8) return 'Giỏi';
      if (score >= 6.5) return 'Khá';
      if (score >= 5) return 'Trung bình';
      return 'Chưa đạt';
    };
    
    // Get overall classification
    const getOverallClassification = (score) => {
      if (score >= 9) return 'Xuất sắc';
      if (score >= 8) return 'Giỏi';
      if (score >= 6.5) return 'Khá';
      if (score >= 5) return 'Trung bình';
      return 'Chưa đạt';
    };
    
    // Calculate average score for a class
    const getAverageScore = (classGrades) => {
      if (!classGrades || classGrades.length === 0) return 0;
      
      let totalWeightedScore = 0;
      let totalWeight = 0;
      
      classGrades.forEach(grade => {
        const gradeType = gradeTypes.value.find(gt => gt.id === grade.grade_type_id);
        
        if (gradeType) {
          totalWeightedScore += grade.score * gradeType.weight;
          totalWeight += gradeType.weight;
        }
      });
      
      return totalWeight > 0 ? totalWeightedScore / totalWeight : 0;
    };
    
    // Calculate overall average for all displayed grades
    const getOverallAverage = (allGrades) => {
      const classIds = [...new Set(allGrades.map(grade => grade.class_id))];
      
      if (classIds.length === 0) return 0;
      
      let totalScore = 0;
      
      classIds.forEach(classId => {
        const classGrades = allGrades.filter(grade => grade.class_id === classId);
        totalScore += getAverageScore(classGrades);
      });
      
      return classIds.length > 0 ? totalScore / classIds.length : 0;
    };
    
    // Show toast message
    const showMessage = (text, type = 'success', title = 'Thông báo') => {
      message.value = text;
      messageType.value = type;
      toastTitle.value = title;
      
      if (!toastInstance) {
        const toastEl = document.getElementById('notification');
        if (toastEl) {
          toastInstance = new Toast(toastEl);
        }
      }
      
      if (toastInstance) {
        toastInstance.show();
      }
    };
    
    // Lifecycle hooks
    onMounted(async () => {
      if (!studentId.value) {
        showMessage('Không tìm thấy thông tin sinh viên. Vui lòng đăng nhập lại.', 'danger');
        return;
      }
      
      await Promise.all([
        fetchGradeTypes(),
        fetchClasses()
      ]);
      
      await fetchGrades();
      
      // Initialize toast
      const toastEl = document.getElementById('notification');
      if (toastEl) {
        toastInstance = new Toast(toastEl);
      }
    });
    
    return {
      loading,
      grades,
      classes,
      gradeTypes,
      selectedClassId,
      displayedGrades,
      groupedGrades,
      message,
      messageType,
      toastTitle,
      
      fetchGrades,
      fetchGradesByClass,
      resetFilters,
      getClassInfo,
      getGradeTypeName,
      getGradeTypeWeight,
      getScoreClass,
      getStatusClass,
      getStatusText,
      getAverageScore,
      getOverallAverage,
      getOverallClassification,
    };
  }
};
</script>

<style scoped>
.student-grades-view {
  padding-bottom: 2rem;
}

/* Header style */
.card-header {
  padding: 0.75rem 1.25rem;
}

/* Table style */
.table th, .table td {
  vertical-align: middle;
}

/* Badge animation */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.badge {
  animation: fadeIn 0.5s ease-in-out;
}

/* Card hover effect */
.card {
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* Summary card styles */
.border.rounded {
  transition: all 0.3s ease;
  border-color: #dee2e6 !important;
}

.border.rounded:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}
</style>
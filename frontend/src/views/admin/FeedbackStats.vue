<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">Báo cáo và thống kê đánh giá của sinh viên</h4>
            <div>
              <button @click="openReportModal" class="btn btn-light btn-sm me-2">
                <i class="bi bi-file-earmark-text me-1"></i> Tạo báo cáo
              </button>
              <button @click="forceRenderCharts" class="btn btn-light btn-sm me-2">
                <i class="bi bi-arrow-clockwise me-1"></i> Cập nhật biểu đồ
              </button>
              <span class="badge bg-light text-dark me-2">
                {{ currentPeriod }}
              </span>
            </div>
          </div>
          <div class="card-body">
            <!-- Bộ lọc -->
            <div class="row g-3 mb-4 align-items-end">
              <div class="col-md-3 col-lg-2">
                <label class="form-label">Năm</label>
                <select class="form-select" v-model="filters.year" @change="applyFilters">
                  <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
                </select>
              </div>
              
              <div class="col-md-3 col-lg-2">
                <label class="form-label">Quý</label>
                <select class="form-select" v-model="filters.quarter" @change="applyFilters">
                  <option value="">Tất cả</option>
                  <option value="1">Quý 1</option>
                  <option value="2">Quý 2</option>
                  <option value="3">Quý 3</option>
                  <option value="4">Quý 4</option>
                </select>
              </div>
              
              <div class="col-md-3 col-lg-2">
                <label class="form-label">Tháng</label>
                <select class="form-select" v-model="filters.month" @change="applyFilters">
                  <option value="">Tất cả</option>
                  <option v-for="month in 12" :key="month" :value="month">Tháng {{ month }}</option>
                </select>
              </div>
              
              <div class="col-md-3 col-lg-2 ms-auto">
                <label class="form-label">&nbsp;</label>
                <button @click="resetFilters" class="btn btn-outline-secondary w-100">
                  <i class="bi bi-x-circle me-1"></i> Bỏ lọc
                </button>
              </div>
            </div>
            
            <!-- Loading indicator -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Đang tải...</span>
              </div>
              <p class="mt-2">Đang tải dữ liệu thống kê...</p>
            </div>
            
            <!-- Báo cáo thống kê -->
            <div v-else class="stats-container">
              <div v-if="statsError" class="alert alert-info text-center py-5">
                <i class="bi bi-info-circle-fill me-2 fs-3"></i>
                <h5 class="mb-3">Không tìm thấy dữ liệu thống kê</h5>
                <p class="mb-0">
                  Chưa có đánh giá nào trong khoảng thời gian đã chọn. Vui lòng thử chọn khoảng thời gian khác hoặc kiểm tra lại sau.
                </p>
              </div>
              
              <div v-else>
                <!-- Tổng quan -->
                <div class="row g-4 mb-4">
                  <div class="col-md-3">
                    <div class="card card-stats h-100 shadow-sm">
                      <div class="card-body d-flex flex-column align-items-center justify-content-center p-4">
                        <div class="icon-bg bg-primary-light rounded-circle mb-3">
                          <i class="bi bi-chat-square-text fs-1 text-primary"></i>
                        </div>
                        <h2 class="mb-1 fw-bold">{{ stats.total_feedbacks || 0 }}</h2>
                        <p class="text-muted mb-0">Tổng số đánh giá</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-md-3">
                    <div class="card card-stats h-100 shadow-sm">
                      <div class="card-body d-flex flex-column align-items-center justify-content-center p-4">
                        <div class="icon-bg bg-success-light rounded-circle mb-3">
                          <i class="bi bi-emoji-smile fs-1 text-success"></i>
                        </div>
                        <h2 class="mb-1 fw-bold">{{ stats.feedback_by_sentiment?.POSITIVE || 0 }}</h2>
                        <p class="text-muted mb-0">Đánh giá tích cực</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-md-3">
                    <div class="card card-stats h-100 shadow-sm">
                      <div class="card-body d-flex flex-column align-items-center justify-content-center p-4">
                        <div class="icon-bg bg-secondary-light rounded-circle mb-3">
                          <i class="bi bi-emoji-neutral fs-1 text-secondary"></i>
                        </div>
                        <h2 class="mb-1 fw-bold">{{ stats.feedback_by_sentiment?.NEUTRAL || 0 }}</h2>
                        <p class="text-muted mb-0">Đánh giá trung lập</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-md-3">
                    <div class="card card-stats h-100 shadow-sm">
                      <div class="card-body d-flex flex-column align-items-center justify-content-center p-4">
                        <div class="icon-bg bg-danger-light rounded-circle mb-3">
                          <i class="bi bi-emoji-frown fs-1 text-danger"></i>
                        </div>
                        <h2 class="mb-1 fw-bold">{{ stats.feedback_by_sentiment?.NEGATIVE || 0 }}</h2>
                        <p class="text-muted mb-0">Đánh giá tiêu cực</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Thông tin nổi bật về giảng viên và phòng học -->
                <div v-if="stats.top_teachers_by_sentiment || stats.top_classrooms_by_sentiment" class="row g-4 mb-4">
                  <!-- Giảng viên nổi bật -->
                  <div class="col-md-6">
                    <div class="card shadow-sm h-100">
                      <div class="card-header bg-light py-3">
                        <h5 class="mb-0">Giảng viên nhận nhiều đánh giá nổi bật</h5>
                      </div>
                      <div class="card-body p-3">
                        <div class="row g-3">
                          <!-- Tích cực nhất -->
                          <div class="col-md-4">
                            <div class="card bg-success-light border-0 h-100">
                              <div class="card-body p-3">
                                <h6 class="card-title d-flex align-items-center">
                                  <i class="bi bi-emoji-smile me-2 text-success"></i>
                                  <span>Tích cực nhất</span>
                                </h6>
                                <div v-if="stats.top_teachers_by_sentiment?.positive">
                                  <h5 class="mb-1">{{ stats.top_teachers_by_sentiment.positive.name }}</h5>
                                  <p class="mb-0 small">
                                    <span class="badge bg-success">{{ stats.top_teachers_by_sentiment.positive.count }} đánh giá</span>
                                  </p>
                                </div>
                                <p v-else class="text-muted small mb-0">Không có dữ liệu</p>
                              </div>
                            </div>
                          </div>
                          
                          <!-- Trung lập nhất -->
                          <div class="col-md-4">
                            <div class="card bg-secondary-light border-0 h-100">
                              <div class="card-body p-3">
                                <h6 class="card-title d-flex align-items-center">
                                  <i class="bi bi-emoji-neutral me-2 text-secondary"></i>
                                  <span>Trung lập nhất</span>
                                </h6>
                                <div v-if="stats.top_teachers_by_sentiment?.neutral">
                                  <h5 class="mb-1">{{ stats.top_teachers_by_sentiment.neutral.name }}</h5>
                                  <p class="mb-0 small">
                                    <span class="badge bg-secondary">{{ stats.top_teachers_by_sentiment.neutral.count }} đánh giá</span>
                                  </p>
                                </div>
                                <p v-else class="text-muted small mb-0">Không có dữ liệu</p>
                              </div>
                            </div>
                          </div>
                          
                          <!-- Tiêu cực nhất -->
                          <div class="col-md-4">
                            <div class="card bg-danger-light border-0 h-100">
                              <div class="card-body p-3">
                                <h6 class="card-title d-flex align-items-center">
                                  <i class="bi bi-emoji-frown me-2 text-danger"></i>
                                  <span>Tiêu cực nhất</span>
                                </h6>
                                <div v-if="stats.top_teachers_by_sentiment?.negative">
                                  <h5 class="mb-1">{{ stats.top_teachers_by_sentiment.negative.name }}</h5>
                                  <p class="mb-0 small">
                                    <span class="badge bg-danger">{{ stats.top_teachers_by_sentiment.negative.count }} đánh giá</span>
                                  </p>
                                </div>
                                <p v-else class="text-muted small mb-0">Không có dữ liệu</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Phòng học nổi bật -->
                  <div class="col-md-6">
                    <div class="card shadow-sm h-100">
                      <div class="card-header bg-light py-3">
                        <h5 class="mb-0">Phòng học nhận nhiều đánh giá nổi bật</h5>
                      </div>
                      <div class="card-body p-3">
                        <div class="row g-3">
                          <!-- Tích cực nhất -->
                          <div class="col-md-4">
                            <div class="card bg-success-light border-0 h-100">
                              <div class="card-body p-3">
                                <h6 class="card-title d-flex align-items-center">
                                  <i class="bi bi-emoji-smile me-2 text-success"></i>
                                  <span>Tích cực nhất</span>
                                </h6>
                                <div v-if="stats.top_classrooms_by_sentiment?.positive">
                                  <h5 class="mb-1">{{ stats.top_classrooms_by_sentiment.positive.name }}</h5>
                                  <p class="mb-0 small">
                                    <span class="badge bg-success">{{ stats.top_classrooms_by_sentiment.positive.count }} đánh giá</span>
                                  </p>
                                </div>
                                <p v-else class="text-muted small mb-0">Không có dữ liệu</p>
                              </div>
                            </div>
                          </div>
                          
                          <!-- Trung lập nhất -->
                          <div class="col-md-4">
                            <div class="card bg-secondary-light border-0 h-100">
                              <div class="card-body p-3">
                                <h6 class="card-title d-flex align-items-center">
                                  <i class="bi bi-emoji-neutral me-2 text-secondary"></i>
                                  <span>Trung lập nhất</span>
                                </h6>
                                <div v-if="stats.top_classrooms_by_sentiment?.neutral">
                                  <h5 class="mb-1">{{ stats.top_classrooms_by_sentiment.neutral.name }}</h5>
                                  <p class="mb-0 small">
                                    <span class="badge bg-secondary">{{ stats.top_classrooms_by_sentiment.neutral.count }} đánh giá</span>
                                  </p>
                                </div>
                                <p v-else class="text-muted small mb-0">Không có dữ liệu</p>
                              </div>
                            </div>
                          </div>
                          
                          <!-- Tiêu cực nhất -->
                          <div class="col-md-4">
                            <div class="card bg-danger-light border-0 h-100">
                              <div class="card-body p-3">
                                <h6 class="card-title d-flex align-items-center">
                                  <i class="bi bi-emoji-frown me-2 text-danger"></i>
                                  <span>Tiêu cực nhất</span>
                                </h6>
                                <div v-if="stats.top_classrooms_by_sentiment?.negative">
                                  <h5 class="mb-1">{{ stats.top_classrooms_by_sentiment.negative.name }}</h5>
                                  <p class="mb-0 small">
                                    <span class="badge bg-danger">{{ stats.top_classrooms_by_sentiment.negative.count }} đánh giá</span>
                                  </p>
                                </div>
                                <p v-else class="text-muted small mb-0">Không có dữ liệu</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Biểu đồ thống kê -->
                <div class="row g-4 mb-4">
                  <!-- Biểu đồ phân loại đánh giá -->
                  <div class="col-md-6">
                    <div class="card shadow-sm h-100">
                      <div class="card-header bg-light py-3">
                        <h5 class="mb-0">Phân loại đánh giá</h5>
                      </div>
                      <div class="card-body">
                        <div style="height: 250px;" class="chart-container">
                          <canvas ref="typeChart"></canvas>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Biểu đồ sentiment -->
                  <div class="col-md-6">
                    <div class="card shadow-sm h-100">
                      <div class="card-header bg-light py-3">
                        <h5 class="mb-0">Phân tích cảm xúc</h5>
                      </div>
                      <div class="card-body">
                        <div style="height: 250px;" class="chart-container">
                          <canvas ref="sentimentChart"></canvas>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Biều đồ xu hướng theo thời gian -->
                <div class="row g-4 mb-4">
                  <div class="col-12">
                    <div class="card shadow-sm">
                      <div class="card-header bg-light py-3">
                        <h5 class="mb-0">Xu hướng đánh giá theo thời gian</h5>
                      </div>
                      <div class="card-body">
                        <div style="height: 200px;" class="chart-container">
                          <canvas ref="timeSeriesChart"></canvas>
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
  </div>

  <!-- Report Modal -->
  <div class="modal fade" id="reportModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title">Tạo báo cáo phản hồi</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <!-- Date selection form -->
          <div v-if="!generatingReport && !reportData">
            <p class="mb-3">Chọn khoảng thời gian để tạo báo cáo phản hồi:</p>
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Ngày bắt đầu <span class="text-danger">*</span></label>
                <VueFlatpickr
                  v-model="reportDates.startDate"
                  class="form-control"
                  placeholder="DD/MM/YYYY"
                  :config="flatpickrConfig"
                  required
                />
              </div>
              <div class="col-md-6">
                <label class="form-label">Ngày kết thúc <span class="text-danger">*</span></label>
                <VueFlatpickr
                  v-model="reportDates.endDate"
                  class="form-control"
                  placeholder="DD/MM/YYYY"
                  :config="flatpickrConfig"
                  required
                />
              </div>
            </div>
            <div class="text-danger mt-2" v-if="reportError">{{ reportError }}</div>
          </div>
          
          <!-- Loading indicator -->
          <div v-if="generatingReport" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Đang tạo báo cáo...</span>
            </div>
            <p class="mt-3">Đang tạo báo cáo từ phản hồi của sinh viên...</p>
            <p class="small text-muted">Quá trình này có thể mất vài phút, vui lòng đợi.</p>
          </div>
          
          <!-- Report result -->
          <div v-if="reportData && !generatingReport" class="report-container">
            <div class="d-flex justify-content-between mb-3">
              <h5>Báo cáo phản hồi {{ reportData.period }}</h5>
              <button @click="downloadReportAsPDF" class="btn btn-sm btn-success">
                <i class="bi bi-download me-1"></i> Tải PDF
              </button>
            </div>
            <div id="reportContent" class="report-content border p-3 bg-light">
              <div v-html="formatReportContent(reportData.report)"></div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="!reportData && !generatingReport" type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
          <button v-if="!reportData && !generatingReport" type="button" class="btn btn-primary" @click="generateReport">
            <i class="bi bi-file-earmark-text me-1"></i> Tạo báo cáo
          </button>
          <button v-if="reportData && !generatingReport" type="button" class="btn btn-secondary" @click="resetReportModal">Tạo báo cáo mới</button>
          <button v-if="reportData && !generatingReport" type="button" class="btn btn-primary" data-bs-dismiss="modal">Đóng</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive, watch, onMounted, onUnmounted, nextTick } from 'vue';
import Chart from 'chart.js/auto';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend, 
  ArcElement 
} from 'chart.js';
import api from '@/utils/api';
import { Modal } from 'bootstrap';
import html2pdf from 'html2pdf.js';
import VueFlatpickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';
import Vietnamese from 'flatpickr/dist/l10n/vn.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default {
  name: 'FeedbackStats',
  
  components: {
    VueFlatpickr
  },
  
  setup() {
    // Khởi tạo biến
    const loading = ref(true);
    const stats = ref({});
    const detailedStats = ref({
      teacher_statistics: [],
      classroom_statistics: []
    });
    const teachers = ref([]);
    const classrooms = ref([]);
    const currentPeriod = ref('');
    const statsError = ref(false);
    
    // Chart references
    const typeChart = ref(null);
    const sentimentChart = ref(null);
    const timeSeriesChart = ref(null);
    
    // Chart instances
    let typeChartInstance = null;
    let sentimentChartInstance = null;
    let timeSeriesChartInstance = null;
    
    // Filters
    const filters = ref({
      year: new Date().getFullYear(),
      month: '',
      quarter: '',
      prevMonth: ''
    });
    
    // Available years for filtering
    const currentYear = new Date().getFullYear();
    const availableYears = ref([currentYear - 2, currentYear - 1, currentYear, currentYear + 1]);
    
    // Helper function to calculate percentage safely
    const calculatePercentage = (part, total) => {
      if (!total || total === 0) return 0;
      return Math.round((part / total) * 100);
    };
    
    // Fetch Stats
    const fetchStats = async () => {
      loading.value = true;
      statsError.value = false;
      
      try {
        // Get authentication token
        const token = localStorage.getItem('auth_token');
        
        // Build query params
        const params = {};
        if (filters.value.year) params.year = filters.value.year;
        if (filters.value.month) params.month = filters.value.month;
        if (filters.value.quarter) params.quarter = filters.value.quarter;
        
        const response = await api.get('/admin/stats/feedback', {
          params,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        stats.value = response.data;
        
        // Update period display
        currentPeriod.value = response.data.period || '';
        
        
      } catch (error) {
        console.error('Error fetching statistics:', error);
        statsError.value = true;
      } finally {
        loading.value = false;
        
        // Update charts after loading is complete
        setTimeout(() => {
          updateCharts();
        }, 100);
      }
    };
    
    // Tạo hàm cập nhật phân trang và fetch dữ liệu mới
    const updateTeacherPage = (newPage) => {
      teacherCurrentPage.value = newPage;
    };
    
    const updateClassroomPage = (newPage) => {
      classroomCurrentPage.value = newPage;
    };
    
    // Thêm các reactive properties cho phân trang
    const teacherTotalItems = ref(0);
    const teacherTotalPages = ref(1);
    const classroomTotalItems = ref(0);
    const classroomTotalPages = ref(1);
    
    // Biến theo dõi sắp xếp
    const teacherSortField = ref('count');
    const teacherSortDirection = ref('desc');
    const classroomSortField = ref('count');
    const classroomSortDirection = ref('desc');
    
    // Cập nhật lọc theo sentiment
    const updateTeacherSentimentFilter = (value) => {
      teacherSentimentFilter.value = value;
      teacherCurrentPage.value = 1;
    };
    
    const updateClassroomSentimentFilter = (value) => {
      classroomSentimentFilter.value = value;
      classroomCurrentPage.value = 1;
    };
    
    // Thêm hàm xử lý sắp xếp khi nhấp vào header cột
    const requestSort = (field, isTeacher = true) => {
      if (isTeacher) {
        // Kiểm tra có đang ở chế độ lọc "Tất cả đánh giá" không
        if (teacherSentimentFilter.value === 'all') {
          return; // Không xử lý sắp xếp nếu đang xem tất cả đánh giá
        }
        
        // Nếu đang sắp xếp theo field này rồi, đảo chiều
        if (teacherSortField.value === field) {
          teacherSortDirection.value = teacherSortDirection.value === 'asc' ? 'desc' : 'asc';
        } else {
          // Nếu chuyển sang field mới, mặc định sắp xếp giảm dần
          teacherSortField.value = field;
          teacherSortDirection.value = 'desc';
        }
        // Reset về trang 1 khi thay đổi cách sắp xếp
        teacherCurrentPage.value = 1;
      } else {
        // Kiểm tra có đang ở chế độ lọc "Tất cả đánh giá" không
        if (classroomSentimentFilter.value === 'all') {
          return; // Không xử lý sắp xếp nếu đang xem tất cả đánh giá
        }
        
        // Xử lý tương tự cho phòng học
        if (classroomSortField.value === field) {
          classroomSortDirection.value = classroomSortDirection.value === 'asc' ? 'desc' : 'asc';
        } else {
          classroomSortField.value = field;
          classroomSortDirection.value = 'desc';
        }
        classroomCurrentPage.value = 1;
      }
    };
    
    // Hàm trả về class cho header cột đang được sắp xếp
    const getSortClass = (field, currentSortField, currentSortDirection) => {
      if (field !== currentSortField) return '';
      return currentSortDirection === 'asc' ? 'sorting-asc' : 'sorting-desc';
    };
    
    // Apply filters and refetch data
    const applyFilters = () => {
      // If month is selected, clear quarter and vice versa
      if (filters.value.month && filters.value.quarter) {
        if (filters.value.month !== filters.value.prevMonth) {
          filters.value.quarter = '';
        } else {
          filters.value.month = '';
        }
      }
      filters.value.prevMonth = filters.value.month;
      
      fetchStats();
    };
    
    // Reset filters
    const resetFilters = () => {
      filters.value = {
        year: new Date().getFullYear(),
        month: '',
        quarter: '',
        prevMonth: ''
      };
      fetchStats();
    };
    
    // Update Charts function
    const updateCharts = () => {
      
      // Ensure the charts are updated after the DOM is ready
      nextTick(async () => {
        try {
          // Destroy previous charts if they exist
          if (typeChartInstance) {
            typeChartInstance.destroy();
          }
          if (sentimentChartInstance) {
            sentimentChartInstance.destroy();
          }
          if (timeSeriesChartInstance) {
            timeSeriesChartInstance.destroy();
          }
          
          // Reset instances
          typeChartInstance = null;
          sentimentChartInstance = null;
          timeSeriesChartInstance = null;
          
          // Wait a bit to ensure DOM is ready
          await new Promise(resolve => setTimeout(resolve, 100));
          
          // Create new charts
          createTypeChart();
          createSentimentChart();
          createTimeSeriesChart();
        } catch (error) {
          console.error('Error updating charts:', error);
        }
      });
    };
    
    // Create Type Chart
    const createTypeChart = () => {
      if (!typeChart.value || !stats.value?.feedback_by_type) {
        console.warn('Cannot create type chart - missing element or data');
        return;
      }
      
      try {
        // Log canvas size
          typeChart.value.clientWidth, 
          typeChart.value.clientHeight
        ;
        
        const ctx = typeChart.value.getContext('2d');
        if (!ctx) {
          console.error('Failed to get 2d context for type chart');
          return;
        }
        
        
        // Get parent div size
        const parentDiv = typeChart.value.parentElement;        
        // Set explicit dimensions on canvas
        typeChart.value.style.width = '100%';
        typeChart.value.style.height = '100%';
        
        typeChartInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Đánh giá giảng viên', 'Đánh giá phòng học'],
            datasets: [{
              data: [
                stats.value.feedback_by_type.TEACHER || 0,
                stats.value.feedback_by_type.CLASSROOM || 0
              ],
              backgroundColor: [
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 159, 64, 0.7)'
              ],
              borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(255, 159, 64, 1)'
              ],
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || '';
                    const value = context.raw || 0;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                    return `${label}: ${value} (${percentage}%)`;
                  }
                }
              }
            }
          }
        });
      } catch (error) {
        console.error('Error creating type chart:', error);
      }
    };
    
    // Create Sentiment Chart
    const createSentimentChart = () => {
      if (!sentimentChart.value || !stats.value?.feedback_by_sentiment) {
        console.warn('Cannot create sentiment chart - missing element or data');
        return;
      }
      
      try {
        const ctx = sentimentChart.value.getContext('2d');
        if (!ctx) {
          console.error('Failed to get 2d context for sentiment chart');
          return;
        }
                
        sentimentChartInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Tích cực', 'Trung lập', 'Tiêu cực'],
            datasets: [{
              data: [
                stats.value.feedback_by_sentiment.POSITIVE || 0,
                stats.value.feedback_by_sentiment.NEUTRAL || 0,
                stats.value.feedback_by_sentiment.NEGATIVE || 0
              ],
              backgroundColor: [
                'rgba(75, 192, 192, 0.7)',
                'rgba(201, 203, 207, 0.7)',
                'rgba(255, 99, 132, 0.7)'
              ],
              borderColor: [
                'rgba(75, 192, 192, 1)',
                'rgba(201, 203, 207, 1)',
                'rgba(255, 99, 132, 1)'
              ],
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || '';
                    const value = context.raw || 0;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                    return `${label}: ${value} (${percentage}%)`;
                  }
                }
              }
            }
          }
        });
      } catch (error) {
        console.error('Error creating sentiment chart:', error);
      }
    };
    
    // Create Time Series Chart
    const createTimeSeriesChart = () => {
      if (!timeSeriesChart.value || !stats.value?.time_series_data) {
        console.warn('Cannot create time series chart - missing element or data');
        return;
      }
      
      try {
        const ctx = timeSeriesChart.value.getContext('2d');
        if (!ctx) {
          console.error('Failed to get 2d context for time series chart');
          return;
        }
                
        timeSeriesChartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: stats.value.time_series_data.map(item => item.period),
            datasets: [{
              label: 'Số lượng đánh giá',
              data: stats.value.time_series_data.map(item => item.count),
              fill: true,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              tension: 0.1,
              pointRadius: 4,
              pointHoverRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `Số lượng: ${context.raw}`;
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  precision: 0
                }
              }
            }
          }
        });
      } catch (error) {
        console.error('Error creating time series chart:', error);
      }
    };
    
    // Initialize on component mount
    onMounted(async () => {
      await fetchStats();
      
      // Add window resize event listener
      window.addEventListener('resize', () => {
        updateCharts();
      });
      
      // Initialize report modal
      reportModal.value = new Modal(document.getElementById('reportModal'));
      
      // Set default date range (last 30 days)
      const today = new Date();
      const lastMonth = new Date();
      lastMonth.setDate(today.getDate() - 30);
      
      reportDates.value.endDate = today.toISOString().split('T')[0];
      reportDates.value.startDate = lastMonth.toISOString().split('T')[0];
    });
    
    // Clean up event listener on unmount
    onUnmounted(() => {
      window.removeEventListener('resize', updateCharts);
      
      // Clean up chart instances
      if (typeChartInstance) typeChartInstance.destroy();
      if (sentimentChartInstance) typeChartInstance.destroy();
      if (timeSeriesChartInstance) timeSeriesChartInstance.destroy();
    });
    
    // Watch for filter changes
    watch(() => [filters.value.year, filters.value.month, filters.value.quarter], () => {
      applyFilters();
    });
    
    // Force render charts
    const forceRenderCharts = () => {
      // Wait for next tick before updating charts
      nextTick(() => {
        // Force update chart parent divs
        const chartDivs = document.querySelectorAll('.chart-container');
        chartDivs.forEach(div => {
          div.style.display = 'none';
          setTimeout(() => {
            div.style.display = 'block';
          }, 10);
        });
        
        // Completely recreate charts
        setTimeout(() => {
          updateCharts();
        }, 100);
      });
    };
    
    // Open report modal
    const openReportModal = () => {
      reportModal.value.show();
    };

    // Add these variables to manage the report generation
    const reportModal = ref(null);
    const reportDates = ref({
      startDate: '',
      endDate: ''
    });
    const reportError = ref('');
    const generatingReport = ref(false);
    const reportData = ref(null);

    // Generate report
    const generateReport = async () => {
      // Validate date inputs
      if (!reportDates.value.startDate || !reportDates.value.endDate) {
        reportError.value = "Vui lòng chọn cả ngày bắt đầu và ngày kết thúc";
        return;
      }
      
      const startDate = new Date(reportDates.value.startDate);
      const endDate = new Date(reportDates.value.endDate);
      
      if (startDate > endDate) {
        reportError.value = "Ngày bắt đầu không thể sau ngày kết thúc";
        return;
      }
      
      // Clear previous error
      reportError.value = '';
      generatingReport.value = true;
      
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.post('http://localhost:5000/api/feedbacks/generate-report', {
          start_date: reportDates.value.startDate,
          end_date: reportDates.value.endDate
        }, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        reportData.value = response.data;
      } catch (error) {
        console.error('Error generating report:', error);
        if (error.response && error.response.data && error.response.data.message) {
          reportError.value = error.response.data.message;
        } else {
          reportError.value = "Không thể tạo báo cáo. Vui lòng thử lại sau.";
        }
      } finally {
        generatingReport.value = false;
      }
    };

    // Reset report modal
    const resetReportModal = () => {
      reportData.value = null;
      reportError.value = '';
      
      // Set default date range (last 30 days)
      const today = new Date();
      const lastMonth = new Date();
      lastMonth.setDate(today.getDate() - 30);
      
      reportDates.value.endDate = today.toISOString().split('T')[0];
      reportDates.value.startDate = lastMonth.toISOString().split('T')[0];
    };

    // Format report content with HTML
    const formatReportContent = (content) => {
      if (!content) return '';
      
      // Replace Markdown headings with HTML headings
      let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
        .replace(/\n\n/g, '<br><br>') // Line breaks
        .replace(/\n/g, '<br>') // Line breaks
        .replace(/---/g, '<hr>') // Horizontal rule
        
        // Replace emoji headers
        .replace(/📅/g, '<span class="report-emoji">📅</span>')
        .replace(/📊/g, '<span class="report-emoji">📊</span>')
        .replace(/📝/g, '<span class="report-emoji">📝</span>')
        .replace(/💡/g, '<span class="report-emoji">💡</span>');
      
      return formattedContent;
    };

    // Download report as PDF
    const downloadReportAsPDF = () => {
      const content = document.getElementById('reportContent');
      
      if (!content) return;
      
      const options = {
        margin: 10,
        filename: `báo_cáo_phản_hồi_${reportDates.value.startDate}_${reportDates.value.endDate}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      
      html2pdf().from(content).set(options).save();
    };

    // Flatpickr configuration
    const flatpickrConfig = {
      dateFormat: 'Y-m-d',
      locale: Vietnamese.vn,
      allowInput: true,
      altFormat: 'd/m/Y',
      altInput: true,
      parseDate: (datestr, format) => {
        // Xử lý khi người dùng nhập 8 số liên tiếp
        if (/^\d{8}$/.test(datestr)) {
          const day = datestr.substring(0, 2);
          const month = datestr.substring(2, 4);
          const year = datestr.substring(4, 8);
          return new Date(`${year}-${month}-${day}`);
        }
        return flatpickr.parseDate(datestr, format);
      }
    };

    return {
      loading,
      stats,
      detailedStats,
      teachers,
      classrooms,
      currentPeriod,
      filters,
      availableYears,
      typeChart,
      sentimentChart,
      timeSeriesChart,
      applyFilters,
      statsError,
      forceRenderCharts,
      resetFilters,
      calculatePercentage,
      openReportModal,
      reportModal,
      reportDates,
      reportError,
      generatingReport,
      reportData,
      resetReportModal,
      formatReportContent,
      downloadReportAsPDF,
      generateReport,
      flatpickrConfig
    };
  }
};
</script>

<style scoped>
.stats-container {
  animation: fadeIn 0.5s ease-in-out;
}

.card-stats {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card-stats:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.icon-bg {
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-primary-light {
  background-color: rgba(13, 110, 253, 0.1);
}

.bg-success-light {
  background-color: rgba(25, 135, 84, 0.1);
}

.bg-secondary-light {
  background-color: rgba(108, 117, 125, 0.1);
}

.bg-danger-light {
  background-color: rgba(220, 53, 69, 0.1);
}

/* Chart container styles */
canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.sortable {
  cursor: pointer;
  position: relative;
  user-select: none;
}

.sortable:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.sorting-asc .bi-arrow-down-up::before {
  content: "\f143"; /* bi-sort-up */
}

.sorting-desc .bi-arrow-down-up::before {
  content: "\f146"; /* bi-sort-down */
}

th:not(.sortable) {
  cursor: default;
}

.report-container {
  max-height: 500px;
  overflow-y: auto;
}

.report-content {
  font-family: Arial, sans-serif;
  line-height: 1.6;
}

.report-emoji {
  font-size: 1.5rem;
  margin-right: 10px;
}

/* Custom styles for the printed report */
@media print {
  .report-content {
    font-size: 12pt;
  }
  
  .report-emoji {
    font-size: 14pt;
  }
}
</style>
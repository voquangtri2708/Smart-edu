<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">Báo cáo và thống kê đánh giá của sinh viên</h4>
            <div>
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
                
                <!-- Chi tiết theo giảng viên và phòng học -->
                <div v-if="detailedStats" class="row g-4">
                  <!-- Top giảng viên theo đánh giá -->
                  <div class="col-12">
                    <div class="card shadow-sm mb-4">
                      <div class="card-header bg-light py-3 d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Top giảng viên theo đánh giá</h5>
                        <div class="d-flex align-items-center">
                          <div class="me-3">
                            <select v-model="teacherSentimentFilter" class="form-select form-select-sm" @change="updateTeacherSentimentFilter(teacherSentimentFilter)">
                              <option value="all">Tất cả đánh giá</option>
                              <option value="positive">Tích cực</option>
                              <option value="neutral">Trung lập</option>
                              <option value="negative">Tiêu cực</option>
                            </select>
                          </div>
                          <span class="badge bg-primary">{{ topTeachersCount }} giảng viên</span>
                        </div>
                      </div>
                      <div class="card-body p-0">
                        <div v-if="loading" class="text-center p-4">
                          <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Đang tải...</span>
                          </div>
                          <p class="mt-2">Đang tải dữ liệu...</p>
                        </div>
                        <div v-else-if="!filteredTopTeachers.length" class="text-center p-4">
                          <i class="bi bi-info-circle-fill text-muted fs-1"></i>
                          <p class="mt-2">Không tìm thấy dữ liệu giảng viên</p>
                        </div>
                        <div v-else class="table-responsive">
                          <table class="table table-hover mb-0">
                            <thead>
                              <tr>
                                <th scope="col" class="ps-3">Giảng viên</th>
                                <th scope="col" class="text-center">Loại đánh giá</th>
                                <th 
                                  scope="col" 
                                  class="text-center"
                                  :class="{ 
                                    'sortable': teacherSentimentFilter !== 'all', 
                                    'sorting-asc': teacherSortField === 'count' && teacherSortDirection === 'asc',
                                    'sorting-desc': teacherSortField === 'count' && teacherSortDirection === 'desc'
                                  }"
                                  @click="teacherSentimentFilter !== 'all' && requestSort('count', true)"
                                >
                                  Số lượng
                                  <i v-if="teacherSentimentFilter !== 'all'" class="bi bi-arrow-down-up ms-1"></i>
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-for="(teacher, index) in filteredTopTeachers" :key="index">
                                <td class="ps-3">{{ teacher.name }}</td>
                                <td class="text-center">
                                  <span :class="getSentimentBadgeClass(teacher.sentiment)">
                                    {{ getSentimentLabel(teacher.sentiment) }}
                                  </span>
                                </td>
                                <td class="text-center">
                                  <strong>{{ teacher.count }}</strong>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                          
                          <!-- Phân trang -->
                          <div class="d-flex justify-content-between align-items-center p-3 border-top">
                            <div>
                              <span class="text-muted">Hiển thị {{ teacherCurrentPage * teacherItemsPerPage - teacherItemsPerPage + 1 }}-{{ Math.min(teacherCurrentPage * teacherItemsPerPage, teacherTotalItems) }} trên {{ teacherTotalItems }} giảng viên</span>
                            </div>
                            <nav aria-label="Điều hướng trang">
                              <ul class="pagination mb-0">
                                <li class="page-item" :class="{ disabled: teacherCurrentPage === 1 }">
                                  <a class="page-link" href="#" @click.prevent="updateTeacherPage(1)" aria-label="Trang đầu">
                                    <span aria-hidden="true">&laquo;</span>
                                  </a>
                                </li>
                                <li class="page-item" :class="{ disabled: teacherCurrentPage === 1 }">
                                  <a class="page-link" href="#" @click.prevent="updateTeacherPage(teacherCurrentPage - 1)" aria-label="Trang trước">
                                    <span aria-hidden="true">&lsaquo;</span>
                                  </a>
                                </li>
                                
                                <!-- Hiển thị số trang -->
                                <li class="page-item" v-for="page in paginationRange(teacherCurrentPage, teacherTotalPages)" :key="page" :class="{ active: page === teacherCurrentPage }">
                                  <a class="page-link" href="#" @click.prevent="updateTeacherPage(page)">{{ page }}</a>
                                </li>
                                
                                <li class="page-item" :class="{ disabled: teacherCurrentPage >= teacherTotalPages }">
                                  <a class="page-link" href="#" @click.prevent="updateTeacherPage(teacherCurrentPage + 1)" aria-label="Trang sau">
                                    <span aria-hidden="true">&rsaquo;</span>
                                  </a>
                                </li>
                                <li class="page-item" :class="{ disabled: teacherCurrentPage >= teacherTotalPages }">
                                  <a class="page-link" href="#" @click.prevent="updateTeacherPage(teacherTotalPages)" aria-label="Trang cuối">
                                    <span aria-hidden="true">&raquo;</span>
                                  </a>
                                </li>
                              </ul>
                            </nav>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Top phòng học -->
                  <div class="col-12">
                    <div class="card shadow-sm mb-4">
                      <div class="card-header bg-light py-3 d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Top phòng học theo đánh giá</h5>
                        <div class="d-flex align-items-center">
                          <div class="me-3">
                            <select v-model="classroomSentimentFilter" class="form-select form-select-sm" @change="updateClassroomSentimentFilter(classroomSentimentFilter)">
                              <option value="all">Tất cả đánh giá</option>
                              <option value="positive">Tích cực</option>
                              <option value="neutral">Trung lập</option>
                              <option value="negative">Tiêu cực</option>
                            </select>
                          </div>
                          <span class="badge bg-primary">{{ topClassroomsCount }} phòng học</span>
                        </div>
                      </div>
                      <div class="card-body p-0">
                        <div v-if="loading" class="text-center p-4">
                          <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Đang tải...</span>
                          </div>
                          <p class="mt-2">Đang tải dữ liệu...</p>
                        </div>
                        <div v-else-if="!filteredTopClassrooms.length" class="text-center p-4">
                          <i class="bi bi-info-circle-fill text-muted fs-1"></i>
                          <p class="mt-2">Không tìm thấy dữ liệu phòng học</p>
                        </div>
                        <div v-else class="table-responsive">
                          <table class="table table-hover mb-0">
                            <thead>
                              <tr>
                                <th scope="col" class="ps-3">Phòng học</th>
                                <th scope="col" class="text-center">Loại đánh giá</th>
                                <th 
                                  scope="col" 
                                  class="text-center"
                                  :class="{ 
                                    'sortable': classroomSentimentFilter !== 'all', 
                                    'sorting-asc': classroomSortField === 'count' && classroomSortDirection === 'asc',
                                    'sorting-desc': classroomSortField === 'count' && classroomSortDirection === 'desc'
                                  }"
                                  @click="classroomSentimentFilter !== 'all' && requestSort('count', false)"
                                >
                                  Số lượng
                                  <i v-if="classroomSentimentFilter !== 'all'" class="bi bi-arrow-down-up ms-1"></i>
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-for="(classroom, index) in filteredTopClassrooms" :key="index">
                                <td class="ps-3">{{ classroom.name }}</td>
                                <td class="text-center">
                                  <span :class="getSentimentBadgeClass(classroom.sentiment)">
                                    {{ getSentimentLabel(classroom.sentiment) }}
                                  </span>
                                </td>
                                <td class="text-center">
                                  <strong>{{ classroom.count }}</strong>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                          
                          <!-- Phân trang -->
                          <div class="d-flex justify-content-between align-items-center p-3 border-top">
                            <div>
                              <span class="text-muted">Hiển thị {{ classroomCurrentPage * classroomItemsPerPage - classroomItemsPerPage + 1 }}-{{ Math.min(classroomCurrentPage * classroomItemsPerPage, classroomTotalItems) }} trên {{ classroomTotalItems }} phòng học</span>
                            </div>
                            <nav aria-label="Điều hướng trang">
                              <ul class="pagination mb-0">
                                <li class="page-item" :class="{ disabled: classroomCurrentPage === 1 }">
                                  <a class="page-link" href="#" @click.prevent="updateClassroomPage(1)" aria-label="Trang đầu">
                                    <span aria-hidden="true">&laquo;</span>
                                  </a>
                                </li>
                                <li class="page-item" :class="{ disabled: classroomCurrentPage === 1 }">
                                  <a class="page-link" href="#" @click.prevent="updateClassroomPage(classroomCurrentPage - 1)" aria-label="Trang trước">
                                    <span aria-hidden="true">&lsaquo;</span>
                                  </a>
                                </li>
                                
                                <!-- Hiển thị số trang -->
                                <li class="page-item" v-for="page in paginationRange(classroomCurrentPage, classroomTotalPages)" :key="page" :class="{ active: page === classroomCurrentPage }">
                                  <a class="page-link" href="#" @click.prevent="updateClassroomPage(page)">{{ page }}</a>
                                </li>
                                
                                <li class="page-item" :class="{ disabled: classroomCurrentPage >= classroomTotalPages }">
                                  <a class="page-link" href="#" @click.prevent="updateClassroomPage(classroomCurrentPage + 1)" aria-label="Trang sau">
                                    <span aria-hidden="true">&rsaquo;</span>
                                  </a>
                                </li>
                                <li class="page-item" :class="{ disabled: classroomCurrentPage >= classroomTotalPages }">
                                  <a class="page-link" href="#" @click.prevent="updateClassroomPage(classroomTotalPages)" aria-label="Trang cuối">
                                    <span aria-hidden="true">&raquo;</span>
                                  </a>
                                </li>
                              </ul>
                            </nav>
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
import axios from 'axios';

// Register Chart components
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
        
        console.log('Fetching stats with params:', params);
        const response = await axios.get('http://localhost:5000/api/admin/stats/feedback', {
          params,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        stats.value = response.data;
        
        // Update period display
        currentPeriod.value = response.data.period || '';
        
        // Fetch detailed stats
        await fetchDetailedStats();
        
        // Check if there are no feedbacks
        if (response.data.total_feedbacks === 0) {
          statsError.value = true;
        }
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
    
    // Fetch Detailed Stats
    const fetchDetailedStats = async () => {
      try {
        // Get authentication token
        const token = localStorage.getItem('auth_token');
        if (!token) {
          console.error('Không tìm thấy token xác thực');
          return;
        }
        
        // Build query params
        const params = {};
        if (filters.value.year) params.year = filters.value.year;
        if (filters.value.month) params.month = filters.value.month;
        if (filters.value.quarter) params.quarter = filters.value.quarter;
        
        // Thêm tham số phân trang và lọc sentiment cho giảng viên
        const teacherParams = { ...params };
        teacherParams.page = teacherCurrentPage.value;
        teacherParams.per_page = teacherItemsPerPage.value;
        
        // Chỉ thêm tham số sắp xếp nếu không phải chế độ "Tất cả đánh giá"
        if (teacherSentimentFilter.value !== 'all') {
          teacherParams.teacher_sort = teacherSortField.value;
          teacherParams.teacher_sort_direction = teacherSortDirection.value;
        }
        
        if (teacherSentimentFilter.value !== 'all') {
          teacherParams.teacher_sentiment = teacherSentimentFilter.value.toUpperCase();
        }
        
        // Thêm tham số phân trang và lọc sentiment cho phòng học
        const classroomParams = { ...params };
        classroomParams.page = classroomCurrentPage.value;
        classroomParams.per_page = classroomItemsPerPage.value;
        
        // Chỉ thêm tham số sắp xếp nếu không phải chế độ "Tất cả đánh giá"
        if (classroomSentimentFilter.value !== 'all') {
          classroomParams.classroom_sort = classroomSortField.value;
          classroomParams.classroom_sort_direction = classroomSortDirection.value;
        }
        
        if (classroomSentimentFilter.value !== 'all') {
          classroomParams.classroom_sentiment = classroomSentimentFilter.value.toUpperCase();
        }
        
        const finalParams = { ...teacherParams, ...classroomParams };
        console.log('API params:', finalParams);
        
        console.log('Fetching detailed stats with params:', { teacherParams, classroomParams });
        const response = await axios.get('http://localhost:5000/api/admin/stats/feedback/detailed', {
          params: finalParams,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        console.log('Detailed stats response:', response.data);
        
        // Ensure detailedStats is initialized with default values if no data is received
        if (!response.data) {
          detailedStats.value = {};
          console.error('No data received from detailed stats API');
        } else {
          detailedStats.value = response.data;
        }
        
        // Load teachers and classrooms for filtering
        if (response.data?.all_teachers?.length > 0) {
          teachers.value = response.data.all_teachers;
          console.log('Loaded teachers:', teachers.value.length);
        }
        
        if (response.data?.all_classrooms?.length > 0) {
          classrooms.value = response.data.all_classrooms;
          console.log('Loaded classrooms:', classrooms.value.length);
        }
        
        // Check pagination info for teachers if available
        if (response.data?.top_teachers_by_sentiment?.pagination) {
          const pagination = response.data.top_teachers_by_sentiment.pagination;
          teacherTotalItems.value = pagination.total;
          teacherTotalPages.value = pagination.pages;
        }
        
        // Check pagination info for classrooms if available
        if (response.data?.top_classrooms_by_sentiment?.pagination) {
          const pagination = response.data.top_classrooms_by_sentiment.pagination;
          classroomTotalItems.value = pagination.total;
          classroomTotalPages.value = pagination.pages;
        }
        
      } catch (error) {
        console.error('Error fetching detailed statistics:', error);
        if (error.response) {
          console.error('Response error:', error.response.data);
        }
        
        // Initialize empty data on error
        detailedStats.value = {};
      } finally {
        loading.value = false;
      }
    };
    
    // Tạo hàm cập nhật phân trang và fetch dữ liệu mới
    const updateTeacherPage = (newPage) => {
      teacherCurrentPage.value = newPage;
      fetchDetailedStats();
    };
    
    const updateClassroomPage = (newPage) => {
      classroomCurrentPage.value = newPage;
      fetchDetailedStats();
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
      teacherCurrentPage.value = 1; // Reset về trang 1 khi thay đổi bộ lọc
      fetchDetailedStats();
    };
    
    const updateClassroomSentimentFilter = (value) => {
      classroomSentimentFilter.value = value;
      classroomCurrentPage.value = 1; // Reset về trang 1 khi thay đổi bộ lọc
      fetchDetailedStats();
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
        console.log('Teacher sort:', teacherSortField.value, teacherSortDirection.value);
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
        console.log('Classroom sort:', classroomSortField.value, classroomSortDirection.value);
      }
      
      // Gọi API để lấy dữ liệu mới theo cách sắp xếp
      fetchDetailedStats();
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
      
      console.log('Applying filters:', filters.value);
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
      console.log('Updating charts with data:', stats.value);
      
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
        console.log('Type chart canvas size before getContext:', 
          typeChart.value.clientWidth, 
          typeChart.value.clientHeight
        );
        
        const ctx = typeChart.value.getContext('2d');
        if (!ctx) {
          console.error('Failed to get 2d context for type chart');
          return;
        }
        
        console.log('Creating type chart with data:', stats.value.feedback_by_type);
        
        // Get parent div size
        const parentDiv = typeChart.value.parentElement;
        console.log('Parent div size:', parentDiv.clientWidth, parentDiv.clientHeight);
        
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
        console.log('Type chart created successfully');
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
        
        console.log('Creating sentiment chart with data:', stats.value.feedback_by_sentiment);
        
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
        console.log('Sentiment chart created successfully');
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
        
        console.log('Creating time series chart with data:', stats.value.time_series_data);
        
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
        console.log('Time series chart created successfully');
      } catch (error) {
        console.error('Error creating time series chart:', error);
      }
    };
    
    // Initialize on component mount
    onMounted(async () => {
      console.log('Component mounted, fetching data...');
      await fetchStats();
      
      // Add window resize event listener
      window.addEventListener('resize', () => {
        updateCharts();
      });
    });
    
    // Clean up event listener on unmount
    onUnmounted(() => {
      window.removeEventListener('resize', updateCharts);
      
      // Clean up chart instances
      if (typeChartInstance) typeChartInstance.destroy();
      if (sentimentChartInstance) sentimentChartInstance.destroy();
      if (timeSeriesChartInstance) timeSeriesChartInstance.destroy();
    });
    
    // Watch for filter changes
    watch(() => [filters.value.year, filters.value.month, filters.value.quarter], () => {
      applyFilters();
    });
    
    // Force render charts
    const forceRenderCharts = () => {
      console.log('Force rendering charts');
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
    
    // Computed properties for sorted data
    const sortedTeacherStatistics = computed(() => {
      if (!detailedStats.value?.teacher_statistics?.length) return [];
      
      return [...detailedStats.value.teacher_statistics]
        .sort((a, b) => {
          // Sort by total_feedbacks in descending order
          return b.total_feedbacks - a.total_feedbacks;
        })
        .map(teacher => {
          // Ensure all required properties exist
          return {
            ...teacher,
            total_feedbacks: teacher.total_feedbacks || 0,
            sentiment_counts: teacher.sentiment_counts || {
              positive: 0, neutral: 0, negative: 0
            },
            sentiment_ratio: teacher.sentiment_ratio || {
              positive: 0, neutral: 0, negative: 0
            }
          };
        })
        .slice(0, 10);
    });
    
    const sortedClassroomStatistics = computed(() => {
      if (!detailedStats.value?.classroom_statistics?.length) return [];
      
      return [...detailedStats.value.classroom_statistics]
        .sort((a, b) => {
          // Sort by total_feedbacks in descending order
          return b.total_feedbacks - a.total_feedbacks;
        })
        .map(classroom => {
          // Ensure all required properties exist
          return {
            ...classroom,
            total_feedbacks: classroom.total_feedbacks || 0,
            sentiment_counts: classroom.sentiment_counts || {
              positive: 0, neutral: 0, negative: 0
            },
            sentiment_ratio: classroom.sentiment_ratio || {
              positive: 0, neutral: 0, negative: 0
            }
          };
        })
        .slice(0, 10);
    });
    
    // Computed properties for counting records with feedback
    const teachersWithFeedback = computed(() => {
      if (!detailedStats.value?.teacher_statistics?.length) return 0;
      
      return detailedStats.value.teacher_statistics.filter(t => t.total_feedbacks > 0).length;
    });
    
    const classroomsWithFeedback = computed(() => {
      if (!detailedStats.value?.classroom_statistics?.length) return 0;
      
      return detailedStats.value.classroom_statistics.filter(c => c.total_feedbacks > 0).length;
    });
    
    // New computed properties for filtering and pagination
    const teacherSentimentFilter = ref('all');
    const classroomSentimentFilter = ref('all');
    const teacherCurrentPage = ref(1);
    const classroomCurrentPage = ref(1);
    const teacherItemsPerPage = ref(10);
    const classroomItemsPerPage = ref(10);
    
    const filteredTopTeachers = computed(() => {
      const result = [];
      
      if (!detailedStats.value?.top_teachers_by_sentiment) return [];
      
      console.log('top_teachers_by_sentiment:', JSON.stringify(detailedStats.value.top_teachers_by_sentiment));
      
      // Nếu đang lọc theo một loại sentiment cụ thể
      if (teacherSentimentFilter.value !== 'all') {
        const sentimentType = teacherSentimentFilter.value.toLowerCase();
        const teachersData = detailedStats.value.top_teachers_by_sentiment[sentimentType] || [];
        
        // Đảm bảo dữ liệu là mảng
        if (Array.isArray(teachersData)) {
          return teachersData;
        }
        return [];
      }
      
      // Trường hợp hiển thị tất cả các loại sentiment
      ['positive', 'neutral', 'negative'].forEach(sentimentType => {
        const teachersData = detailedStats.value.top_teachers_by_sentiment[sentimentType] || [];
        
        // Đảm bảo dữ liệu là mảng
        if (Array.isArray(teachersData)) {
          teachersData.forEach(teacher => {
            result.push(teacher);
          });
        }
      });
      
      // Sắp xếp theo số lượng
      result.sort((a, b) => b.count - a.count);
      
      return result;
    });
    
    const filteredTopClassrooms = computed(() => {
      const result = [];
      
      if (!detailedStats.value?.top_classrooms_by_sentiment) return [];
      
      console.log('top_classrooms_by_sentiment:', JSON.stringify(detailedStats.value.top_classrooms_by_sentiment));
      
      // Nếu đang lọc theo một loại sentiment cụ thể
      if (classroomSentimentFilter.value !== 'all') {
        const sentimentType = classroomSentimentFilter.value.toLowerCase();
        const classroomsData = detailedStats.value.top_classrooms_by_sentiment[sentimentType] || [];
        
        // Đảm bảo dữ liệu là mảng
        if (Array.isArray(classroomsData)) {
          return classroomsData;
        }
        return [];
      }
      
      // Trường hợp hiển thị tất cả các loại sentiment
      ['positive', 'neutral', 'negative'].forEach(sentimentType => {
        const classroomsData = detailedStats.value.top_classrooms_by_sentiment[sentimentType] || [];
        
        // Đảm bảo dữ liệu là mảng
        if (Array.isArray(classroomsData)) {
          classroomsData.forEach(classroom => {
            result.push(classroom);
          });
        }
      });
      
      // Sắp xếp theo số lượng
      result.sort((a, b) => b.count - a.count);
      
      return result;
    });
    
    const topTeachersCount = computed(() => {
      if (!detailedStats.value?.top_teachers_by_sentiment) return 0;
      
      let count = 0;
      
      // Đếm số lượng giảng viên cho từng loại sentiment
      ['positive', 'neutral', 'negative'].forEach(sentimentType => {
        const teachers = detailedStats.value.top_teachers_by_sentiment[sentimentType];
        if (Array.isArray(teachers)) {
          count += teachers.length;
        }
      });
      
      return count;
    });
    
    const topClassroomsCount = computed(() => {
      if (!detailedStats.value?.top_classrooms_by_sentiment) return 0;
      
      let count = 0;
      
      // Đếm số lượng phòng học cho từng loại sentiment
      ['positive', 'neutral', 'negative'].forEach(sentimentType => {
        const classrooms = detailedStats.value.top_classrooms_by_sentiment[sentimentType];
        if (Array.isArray(classrooms)) {
          count += classrooms.length;
        }
      });
      
      return count;
    });
    
    // Helper function to get sentiment badge class
    const getSentimentBadgeClass = (sentiment) => {
      switch (sentiment) {
        case 'positive':
          return 'text-success';
        case 'neutral':
          return 'text-secondary';
        case 'negative':
          return 'text-danger';
        default:
          return '';
      }
    };

    
    // Helper function to get sentiment label
    const getSentimentLabel = (sentiment) => {
      switch (sentiment) {
        case 'positive':
          return 'Tích cực';
        case 'neutral':
          return 'Trung lập';
        case 'negative':
          return 'Tiêu cực';
        default:
          return '';
      }
    };
    
    // Helper function to get pagination range
    const paginationRange = (currentPage, totalPages) => {
      // Hiển thị tối đa 5 trang
      const delta = 2;
      const range = [];
      
      // Tính toán phạm vi hiển thị
      const rangeStart = Math.max(1, currentPage - delta);
      const rangeEnd = Math.min(totalPages, currentPage + delta);
      
      // Thêm các trang vào mảng
      for (let i = rangeStart; i <= rangeEnd; i++) {
        range.push(i);
      }
      
      return range;
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
      sortedTeacherStatistics,
      sortedClassroomStatistics,
      teachersWithFeedback,
      classroomsWithFeedback,
      teacherSentimentFilter,
      classroomSentimentFilter,
      teacherCurrentPage,
      classroomCurrentPage,
      teacherItemsPerPage,
      classroomItemsPerPage,
      filteredTopTeachers,
      filteredTopClassrooms,
      getSentimentBadgeClass,
      getSentimentLabel,
      updateTeacherPage,
      updateClassroomPage,
      teacherTotalItems,
      teacherTotalPages,
      classroomTotalItems,
      classroomTotalPages,
      updateTeacherSentimentFilter,
      updateClassroomSentimentFilter,
      topTeachersCount,
      topClassroomsCount,
      paginationRange,
      teacherSortField,
      teacherSortDirection,
      classroomSortField,
      classroomSortDirection,
      requestSort,
      getSortClass
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
</style> 
<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">Quản lý đánh giá</h4>
            <div>
              <span class="badge bg-light text-dark me-2">
                {{ statisticsText }}
              </span>
            </div>
          </div>
          <div class="card-body">
            <!-- Bộ lọc -->
            <div class="row g-3 mb-4">
              <!-- Lọc loại đánh giá -->
              <div class="col-md-3">
                <label class="form-label">Loại đánh giá</label>
                <select class="form-select" v-model="filters.feedbackType" @change="fetchFeedbacks">
                  <option value="all">Tất cả</option>
                  <option value="TEACHER">Đánh giá giảng viên</option>
                  <option value="CLASSROOM">Đánh giá phòng học</option>
                </select>
              </div>
              
              <!-- Lọc sentiment -->
              <div class="col-md-3">
                <label class="form-label">Sentiment</label>
                <select class="form-select" v-model="filters.sentiment" @change="fetchFeedbacks">
                  <option value="">Tất cả</option>
                  <option value="POSITIVE">Tích cực</option>
                  <option value="NEUTRAL">Trung lập</option>
                  <option value="NEGATIVE">Tiêu cực</option>
                </select>
              </div>
              
              <!-- Lọc thời gian -->
              <div class="col-md-3">
                <label class="form-label">Thời gian</label>
                <select class="form-select" v-model="filters.timeFrame" @change="fetchFeedbacks">
                  <option value="all">Tất cả</option>
                  <option value="lastDay">24 giờ qua</option>
                  <option value="lastWeek">7 ngày qua</option>
                  <option value="lastMonth">30 ngày qua</option>
                </select>
              </div>
              
              <!-- Tìm kiếm -->
              <div class="col-md-3">
                <label class="form-label">Tìm kiếm</label>
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control" 
                    placeholder="Tìm kiếm..." 
                    v-model="filters.searchTerm"
                    @input="onSearchInput"
                  >
                  <button class="btn btn-outline-primary" type="button" @click="fetchFeedbacks">
                    <i class="bi bi-search"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- Tab navigation -->
            <ul class="nav nav-tabs mb-3">
              <li class="nav-item">
                <a 
                  class="nav-link" 
                  :class="{ active: activeTab === 'all' }" 
                  href="#"
                  @click.prevent="activeTab = 'all'; filters.sentiment = ''; fetchFeedbacks();"
                >
                  <i class="bi bi-list me-1"></i> Tất cả
                </a>
              </li>
              <li class="nav-item">
                <a 
                  class="nav-link" 
                  :class="{ active: activeTab === 'POSITIVE' }" 
                  href="#"
                  @click.prevent="activeTab = 'POSITIVE'; filters.sentiment = 'POSITIVE'; fetchFeedbacks();"
                >
                  <i class="bi bi-emoji-smile me-1"></i> Tích cực
                  <span class="badge bg-success ms-1">{{ positiveCount }}</span>
                </a>
              </li>
              <li class="nav-item">
                <a 
                  class="nav-link" 
                  :class="{ active: activeTab === 'NEUTRAL' }" 
                  href="#"
                  @click.prevent="activeTab = 'NEUTRAL'; filters.sentiment = 'NEUTRAL'; fetchFeedbacks();"
                >
                  <i class="bi bi-emoji-neutral me-1"></i> Trung lập
                  <span class="badge bg-secondary ms-1">{{ neutralCount }}</span>
                </a>
              </li>
              <li class="nav-item">
                <a 
                  class="nav-link" 
                  :class="{ active: activeTab === 'NEGATIVE' }" 
                  href="#"
                  @click.prevent="activeTab = 'NEGATIVE'; filters.sentiment = 'NEGATIVE'; fetchFeedbacks();"
                >
                  <i class="bi bi-emoji-frown me-1"></i> Tiêu cực
                  <span class="badge bg-danger ms-1">{{ negativeCount }}</span>
                </a>
              </li>
            </ul>

            <!-- Hiển thị đánh giá -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Đang tải...</span>
              </div>
              <p class="mt-2">Đang tải dữ liệu...</p>
            </div>
            
            <div v-else>
              <div v-if="feedbacks.length > 0">
                <div class="row g-4">
                  <div v-for="feedback in feedbacks" :key="feedback.id" class="col-md-6 col-lg-4">
                    <div 
                      class="card h-100 border-0 shadow-sm hover-card" 
                      :class="{
                        'border-start border-5 border-success': feedback.sentiment === 'POSITIVE',
                        'border-start border-5 border-secondary': feedback.sentiment === 'NEUTRAL',
                        'border-start border-5 border-danger': feedback.sentiment === 'NEGATIVE'
                      }"
                      @click="showFeedbackDetail(feedback.id)"
                      style="cursor: pointer;"
                    >
                      <div class="card-header bg-light d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                          <i 
                            class="bi me-2" 
                            :class="{
                              'bi-person-video3 text-primary': feedback.feedback_type === 'TEACHER',
                              'bi-building text-success': feedback.feedback_type === 'CLASSROOM'
                            }"
                          ></i>
                          <h6 class="mb-0">
                            {{ feedback.feedback_type === 'TEACHER' ? 'Đánh giá giảng viên' : 'Đánh giá phòng học' }}
                          </h6>
                        </div>
                        <span 
                          class="badge" 
                          :class="{
                            'bg-success': feedback.sentiment === 'POSITIVE',
                            'bg-secondary': feedback.sentiment === 'NEUTRAL',
                            'bg-danger': feedback.sentiment === 'NEGATIVE'
                          }"
                        >
                          {{ formatSentiment(feedback.sentiment) }}
                        </span>
                      </div>
                      <div class="card-body">
                        <div class="mb-3">
                          <p class="card-text mb-1">
                            <strong>Thời gian:</strong> {{ formatDate(feedback.created_at) }}
                          </p>
                          <p class="card-text mb-1">
                            <strong>Lớp học: </strong> 
                            <span v-if="feedback.class_info">
                              {{ feedback.class_info.class_code }} - {{ feedback.class_info.subject_name || 'Không có tên môn học' }}
                            </span>
                            <span v-else>{{ feedback.class_id }}</span>
                          </p>
                          <p class="card-text mb-1">
                            <strong>Mã sinh viên:</strong> {{ feedback.student_id }}
                          </p>
                          <p v-if="feedback.teacher_id" class="card-text mb-1">
                            <strong>Giảng viên:</strong> {{ feedback.teacher_info.name }} - {{ feedback.teacher_info.id }}
                          </p>
                          <p class="card-text mb-1">
                            <strong v-if="feedback.classroom_id">Phòng học: </strong> 
                            <span v-if="feedback.classroom_id">
                              {{ feedback.classroom_info.room_number }} - {{ feedback.classroom_info.building_name }} - {{ feedback.classroom_info.campus_name }}
                            </span>
                        </p>
                        </div>
                        
                        <div class="mb-3 feedback-content">
                          <h6 class="fw-bold">Nội dung đánh giá:</h6>
                          <p class="card-text">{{ feedback.content }}</p>
                        </div>
                      </div>
                      
                      <div class="card-footer bg-white border-top-0">
                        <button 
                          class="btn btn-sm btn-outline-danger" 
                          @click.stop="confirmDelete(feedback)"
                        >
                          <i class="bi bi-trash me-1"></i> Xóa đánh giá
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Phân trang -->
                <div class="d-flex justify-content-center mt-4">
                  <nav>
                    <ul class="pagination">
                      <li class="page-item" :class="{ disabled: currentPage === 1 }">
                        <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">
                          <i class="bi bi-chevron-left"></i>
                        </a>
                      </li>
                      <li 
                        v-for="page in totalPages" 
                        :key="page" 
                        class="page-item"
                        :class="{ active: page === currentPage }"
                      >
                        <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
                      </li>
                      <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                        <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">
                          <i class="bi bi-chevron-right"></i>
                        </a>
                      </li>
                    </ul>
                  </nav>
                </div>
              </div>
              
              <div v-else class="text-center py-5">
                <i class="bi bi-inbox display-1 text-muted"></i>
                <h5 class="mt-3">Không có đánh giá nào</h5>
                <p class="text-muted">Không tìm thấy đánh giá nào phù hợp với điều kiện lọc</p>
                <button class="btn btn-outline-primary" @click="resetFilters">
                  <i class="bi bi-arrow-counterclockwise me-1"></i> Đặt lại bộ lọc
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal xác nhận xóa -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true" style="z-index: 1060;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa đánh giá này không?</p>
            <p class="mb-1">
              <strong>Loại đánh giá:</strong>  
              {{ selectedFeedback && selectedFeedback.feedback_type === 'TEACHER' ? 'Đánh giá giảng viên' : 'Đánh giá phòng học' }}
            </p>
            <p class="mb-1">
              <strong>Mã sinh viên:</strong> {{ selectedFeedback?.student_id }}
            </p>
            <p class="mb-0">
              <strong>Nội dung:</strong> {{ selectedFeedback?.content }}
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteFeedback">
              <i class="bi bi-trash me-1"></i> Xóa
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal chi tiết đánh giá -->
    <div class="modal fade" id="detailModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header" 
            :class="{
              'bg-success text-white': detailedFeedback?.sentiment === 'POSITIVE',
              'bg-secondary text-white': detailedFeedback?.sentiment === 'NEUTRAL',
              'bg-danger text-white': detailedFeedback?.sentiment === 'NEGATIVE'
            }">
            <h5 class="modal-title">Chi tiết đánh giá</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingDetail" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Đang tải...</span>
              </div>
              <p class="mt-2">Đang tải thông tin chi tiết...</p>
            </div>
            
            <div v-else-if="detailedFeedback" class="p-2">
              <div class="mb-4">
                <div class="d-flex align-items-center mb-3">
                  <span class="badge me-2" 
                    :class="{
                      'bg-success': detailedFeedback.sentiment === 'POSITIVE',
                      'bg-secondary': detailedFeedback.sentiment === 'NEUTRAL',
                      'bg-danger': detailedFeedback.sentiment === 'NEGATIVE'
                    }"
                    style="font-size: 0.9rem; padding: 8px;"
                  >
                    {{ formatSentiment(detailedFeedback.sentiment) }}
                  </span>
                  <h5 class="mb-0">
                    <i class="bi me-2" 
                      :class="{
                        'bi-person-video3 text-primary': detailedFeedback.feedback_type === 'TEACHER',
                        'bi-building text-success': detailedFeedback.feedback_type === 'CLASSROOM'
                      }"
                    ></i>
                    {{ detailedFeedback.feedback_type === 'TEACHER' ? 'Đánh giá giảng viên' : 'Đánh giá phòng học' }}
                  </h5>
                </div>
                
                <div class="card bg-light">
                  <div class="card-body py-3">
                    <h6 class="fw-bold mb-2">Nội dung đánh giá:</h6>
                    <p class="mb-0">{{ detailedFeedback.content }}</p>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <h6 class="fw-bold border-bottom pb-2 mb-3">Thông tin chung</h6>
                  <p class="mb-2">
                    <strong>Thời gian tạo:</strong> {{ formatDate(detailedFeedback.created_at) }}
                  </p>
                  <p class="mb-2">
                    <strong>Mã sinh viên:</strong> {{ detailedFeedback.student_id }}
                  </p>
                </div>
                
                <div class="col-md-6">
                  <h6 class="fw-bold border-bottom pb-2 mb-3">Thông tin lớp học</h6>
                  <p class="mb-2" v-if="detailedFeedback.class_info">
                    <strong>Mã lớp:</strong> {{ detailedFeedback.class_info.class_code }}
                  </p>
                  <p class="mb-2" v-if="detailedFeedback.class_info && detailedFeedback.class_info.subject_name">
                    <strong>Tên môn học:</strong> {{ detailedFeedback.class_info.subject_name }}
                  </p>
                  <p class="mb-2">
                    <strong>Thời gian đánh giá:</strong> {{ formatDate(detailedFeedback.start_date) }} đến {{ formatDate(detailedFeedback.end_date) }}
                  </p>
                </div>
              </div>
              
              <div class="row mt-3" v-if="detailedFeedback.feedback_type === 'TEACHER' && detailedFeedback.teacher_info">
                <div class="col-12">
                  <h6 class="fw-bold border-bottom pb-2 mb-3">Thông tin giảng viên</h6>
                  <p class="mb-2">
                    <strong>Mã giảng viên:</strong> {{ detailedFeedback.teacher_id }}
                  </p>
                  <p class="mb-2">
                    <strong>Tên giảng viên:</strong> {{ detailedFeedback.teacher_info.name }}
                  </p>
                </div>
              </div>
              
              <div class="row mt-3" v-if="detailedFeedback.feedback_type === 'CLASSROOM' && detailedFeedback.classroom_info">
                <div class="col-12">
                  <h6 class="fw-bold border-bottom pb-2 mb-3">Thông tin phòng học</h6>
                  <p class="mb-2">
                    <strong>Mã phòng:</strong> {{ detailedFeedback.classroom_id }}
                  </p>
                  <p class="mb-2">
                    <strong>Số phòng:</strong> {{ detailedFeedback.classroom_info.room_number }}
                  </p>
                  <p class="mb-2" v-if="detailedFeedback.classroom_info.building_name">
                    <strong>Tòa nhà:</strong> {{ detailedFeedback.classroom_info.building_name }}
                  </p>
                  <p class="mb-2" v-if="detailedFeedback.classroom_info.campus_name">
                    <strong>Cơ sở:</strong> {{ detailedFeedback.classroom_info.campus_name }}
                  </p>
                </div>
              </div>
            </div>
            
            <div v-else class="alert alert-warning">
              <i class="bi bi-exclamation-triangle me-2"></i> 
              Không thể tải thông tin chi tiết của đánh giá
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="confirmDelete(detailedFeedback)"
              v-if="detailedFeedback"
            >
              <i class="bi bi-trash me-1"></i> Xóa đánh giá
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast notification -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
      <div 
        class="toast align-items-center text-white border-0"
        :class="`bg-${toastType}`"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        ref="toast"
      >
        <div class="d-flex">
          <div class="toast-body">
            {{ toastMessage }}
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
import { Modal, Toast } from 'bootstrap';
import { debounce } from '@/utils/debounce';

// Biến lưu trữ dữ liệu
const feedbacks = ref([]);
const loading = ref(true);
const activeTab = ref('all');
const selectedFeedback = ref(null);
const deleteModal = ref(null);
const detailModal = ref(null);
const toast = ref(null);
const toastMessage = ref('');
const toastType = ref('success');

// Biến lưu trữ chi tiết đánh giá
const detailedFeedback = ref(null);
const loadingDetail = ref(false);

// Biến lưu trữ bộ lọc
const filters = ref({
  feedbackType: 'all', // 'all', 'TEACHER', 'CLASSROOM'
  sentiment: '',       // 'POSITIVE', 'NEUTRAL', 'NEGATIVE'
  timeFrame: 'all',    // 'all', 'lastDay', 'lastWeek', 'lastMonth'
  searchTerm: ''
});

// Biến cho phân trang
const currentPage = ref(1);
const pageSize = ref(12);
const totalItems = ref(0);
const totalPages = ref(0);

// Biến lưu trữ số lượng từng loại sentiment
const positiveCount = ref(0);
const neutralCount = ref(0);
const negativeCount = ref(0);

// Computed property cho thống kê
const statisticsText = computed(() => {
  return `Tổng: ${totalItems.value} | Tích cực: ${positiveCount.value} | Trung lập: ${neutralCount.value} | Tiêu cực: ${negativeCount.value}`;
});

// Hàm tính toán số lượng từng loại sentiment từ dữ liệu đầy đủ
const calculateSentimentCounts = async () => {
  try {
    // Lấy token xác thực
    const token = localStorage.getItem('auth_token');
    
    // Gọi API riêng để lấy thống kê sentiment
    const params = {};
    if (filters.value.feedbackType !== 'all') {
      params.feedback_type = filters.value.feedbackType;
    }
    
    if (filters.value.timeFrame !== 'all') {
      // Thời gian được xử lý trong frontend
      params.time_frame = filters.value.timeFrame;
    }
    
    if (filters.value.searchTerm) {
      params.query = filters.value.searchTerm;
    }
    
    // Gọi API không phân trang để lấy số lượng
    const response = await axios.get('http://localhost:5000/api/feedbacks', {
      params: {
        ...params,
        per_page: 1000 // Lấy số lượng lớn để tính toán thống kê
      },
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    // Tính toán sentiment từ dữ liệu trả về
    const allFeedbacks = response.data.items;
    positiveCount.value = allFeedbacks.filter(f => f.sentiment === 'POSITIVE').length;
    neutralCount.value = allFeedbacks.filter(f => f.sentiment === 'NEUTRAL').length;
    negativeCount.value = allFeedbacks.filter(f => f.sentiment === 'NEGATIVE').length;
  } catch (error) {
    console.error('Lỗi khi tải dữ liệu thống kê:', error);
  }
};

// Hàm lấy dữ liệu đánh giá
const fetchFeedbacks = async () => {
  loading.value = true;

  try {
    // Lấy token xác thực
    const token = localStorage.getItem('auth_token');
    
    // Tạo object cho parameters
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    };
    
    // Thêm các tham số lọc vào params
    if (filters.value.feedbackType !== 'all') {
      params.feedback_type = filters.value.feedbackType;
    }
    
    if (filters.value.sentiment) {
      params.sentiment = filters.value.sentiment;
    }
    
    // Xử lý tìm kiếm
    if (filters.value.searchTerm) {
      params.query = filters.value.searchTerm;
    }
    
    // Lấy dữ liệu từ API mới với phân trang
    const response = await axios.get('http://localhost:5000/api/feedbacks', { 
      params,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    // Cập nhật dữ liệu và thông tin phân trang
    feedbacks.value = response.data.items;
    totalItems.value = response.data.pagination.total;
    totalPages.value = response.data.pagination.pages;
    
    // Lọc theo thời gian nếu cần
    // Vì thời gian không xử lý ở backend, nên vẫn phải lọc ở frontend
    if (filters.value.timeFrame !== 'all') {
      const now = new Date();
      let cutoffDate;
      
      switch (filters.value.timeFrame) {
        case 'lastDay':
          cutoffDate = new Date(now.getTime() - (24 * 60 * 60 * 1000));
          break;
        case 'lastWeek':
          cutoffDate = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
          break;
        case 'lastMonth':
          cutoffDate = new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000));
          break;
      }
      
      feedbacks.value = feedbacks.value.filter(feedback => 
        new Date(feedback.created_at) >= cutoffDate
      );
    }
    
    // Cập nhật số lượng sentiment
    await calculateSentimentCounts();
    
  } catch (error) {
    console.error('Lỗi khi tải dữ liệu đánh giá:', error);
    showToast('Không thể tải dữ liệu đánh giá', 'danger');
  } finally {
    loading.value = false;
  }
};

// Hàm xóa đánh giá
const deleteFeedback = async () => {
  if (!selectedFeedback.value) return;
  
  try {
    // Lấy token xác thực
    const token = localStorage.getItem('auth_token');
    
    // Sử dụng API mới để xóa feedback
    await axios.delete(`http://localhost:5000/api/feedbacks/${selectedFeedback.value.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    await fetchFeedbacks();
    showToast('Đã xóa đánh giá thành công', 'success');
    
    // Đóng modal xác nhận xóa
    deleteModal.value.hide();
    
    // Đóng modal chi tiết nếu đang mở
    if (detailModal.value && detailedFeedback.value && detailedFeedback.value.id === selectedFeedback.value.id) {
      detailModal.value.hide();
    }
  } catch (error) {
    console.error('Lỗi khi xóa đánh giá:', error);
    showToast('Không thể xóa đánh giá', 'danger');
  }
};

// Hàm hiển thị modal xác nhận xóa
const confirmDelete = (feedback) => {
  selectedFeedback.value = feedback;
  deleteModal.value.show();
};

// Hàm chuyển đổi trang
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchFeedbacks();
};

// Hàm reset bộ lọc
const resetFilters = () => {
  filters.value = {
    feedbackType: 'all',
    sentiment: '',
    timeFrame: 'all',
    searchTerm: ''
  };
  activeTab.value = 'all';
  currentPage.value = 1;
  fetchFeedbacks();
};

// Direct handler for input event
const onSearchInput = () => {
  debouncedSearch();
};

// Create a debounced search function
const debouncedSearch = debounce(() => {
  currentPage.value = 1;
  fetchFeedbacks();
}, 500);

// Hàm hiển thị toast
const showToast = (message, type = 'info') => {
  toastMessage.value = message;
  toastType.value = type;
  
  if (toast.value) {
    const bsToast = new Toast(toast.value);
    bsToast.show();
  }
};

// Hàm định dạng sentiment
const formatSentiment = (sentiment) => {
  switch (sentiment) {
    case 'POSITIVE': return 'Tích cực';
    case 'NEUTRAL': return 'Trung lập';
    case 'NEGATIVE': return 'Tiêu cực';
    default: return sentiment;
  }
};

// Hàm định dạng ngày
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Hàm hiển thị chi tiết đánh giá
const showFeedbackDetail = async (id) => {
  loadingDetail.value = true;
  detailedFeedback.value = null;
  
  // Hiển thị modal
  detailModal.value.show();
  
  try {
    // Lấy token xác thực
    const token = localStorage.getItem('auth_token');
    
    // Lấy chi tiết đánh giá từ API
    const response = await axios.get(`http://localhost:5000/api/feedbacks/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    detailedFeedback.value = response.data;
  } catch (error) {
    console.error('Lỗi khi tải chi tiết đánh giá:', error);
    showToast('Không thể tải chi tiết đánh giá', 'danger');
  } finally {
    loadingDetail.value = false;
  }
};

// Khởi tạo các component khi mounted
onMounted(async () => {
  // Khởi tạo Bootstrap Modal
  deleteModal.value = new Modal(document.getElementById('deleteModal'));
  detailModal.value = new Modal(document.getElementById('detailModal'));
  
  // Tải dữ liệu đánh giá theo bộ lọc
  await fetchFeedbacks();
});
</script>

<style scoped>
.hover-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.feedback-content {
  max-height: 200px;
  overflow-y: auto;
}

/* Biến đổi các sentiment badge */
.badge.bg-success {
  background-color: #198754 !important;
}

.badge.bg-secondary {
  background-color: #6c757d !important;
}

.badge.bg-danger {
  background-color: #dc3545 !important;
}

/* Style cho phân trang */
.pagination .page-link {
  color: #0d6efd;
}

.pagination .page-item.active .page-link {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
}

/* Responsive styles */
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
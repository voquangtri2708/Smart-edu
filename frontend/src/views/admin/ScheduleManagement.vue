<template>
  <div class="schedule-management">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Quản Lý Lịch Học</h4>
        <button @click="showAddForm = true" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i>Thêm Lịch Học Mới
        </button>
      </div>
      
      <div class="card-body">
        <!-- Hiển thị thông báo -->
        <div v-if="message" :class="'alert alert-' + messageType" role="alert">
          <div class="d-flex align-items-start">
            <i :class="getAlertIcon" class="me-2 mt-1 fs-5"></i>
            <div>
              <span v-if="!hasDetails">{{ message }}</span>
              <template v-else>
                <strong>{{ messageTitle }}</strong>
                <ul class="mb-0 mt-1">
                  <li v-for="(detail, index) in messageDetails" :key="index">
                    {{ detail }}
                  </li>
                </ul>
              </template>
            </div>
          </div>
        </div>
        
        <!-- Search and filter -->
        <div class="row mb-3">
          <div class="col-md-4">
            <label class="form-label">Lớp học</label>
            <select v-model="filters.class_id" class="form-select">
              <option value="">Tất cả lớp học</option>
              <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
                {{ classItem.code }} - {{ getSubjectName(classItem.subject_id) }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Phòng học</label>
            <select v-model="filters.classroom_id" class="form-select">
              <option value="">Tất cả phòng học</option>
              <option v-for="classroom in classrooms" :key="classroom.id" :value="classroom.id">
                {{ classroom.room_number }} - {{ getBuildingName(classroom.building_id) }} ({{ getCampusName(getBuildingCampusId(classroom.building_id)) }})
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Ngày</label>
            <div class="d-flex">
              <VueFlatpickr
                v-model="filters.specific_date"
                class="form-control flex-grow-1"
                placeholder="Chọn ngày cụ thể"
                :config="flatpickrConfig"
              />
              <button @click="fetchSchedules" class="btn btn-primary ms-2 flex-shrink-0">
                <i class="bi bi-search me-1"></i>Lọc
              </button>
            </div>
          </div>
        </div>
        
        <!-- Loading spinner -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Đang tải dữ liệu...</p>
        </div>
        
        <!-- Schedule table -->
        <div v-else-if="schedules.length" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Lớp học</th>
                <th scope="col">Môn học</th>
                <th scope="col">Phòng học</th>
                <th scope="col">Tòa nhà - Cơ sở</th>
                <th scope="col">Ngày trong tuần</th>
                <th scope="col">Thời gian</th>
                <th scope="col">Ngày cụ thể</th>
                <th scope="col">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(schedule, index) in schedules" :key="schedule.id">
                <td>{{ (currentPage - 1) * perPage + index + 1 }}</td>
                <td>{{ schedule.class_code || getClassName(schedule.class_id) }}</td>
                <td>{{ schedule.subject_name || getSubjectName(schedule.subject_id) }}</td>
                <td>{{ schedule.classroom_number || getClassroomName(schedule.classroom_id) }}</td>
                <td>
                  {{ schedule.building_name || getBuildingName(schedule.building_id) }} - 
                  {{ schedule.campus_name || getCampusName(schedule.campus_id) }}
                </td>
                <td>{{ getDayOfWeekText(schedule.day_of_week) }}</td>
                <td>{{ schedule.start_time }} - {{ schedule.end_time }}</td>
                <td>{{ schedule.specific_date || 'Không có' }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button @click="editSchedule(schedule)" class="btn btn-outline-primary" title="Sửa">
                      <i class="bi bi-pencil-square"></i>
                    </button>
                    <button @click="deleteSchedule(schedule.id)" class="btn btn-outline-danger" title="Xóa">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Pagination -->
          <div class="d-flex justify-content-between align-items-center mt-3">
            <div>
              <span>Hiển thị</span>
              <select v-model="perPage" class="form-select d-inline-block mx-2" style="width: auto;" @change="changePerPage">
                <option :value="5">5</option>
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
              <span>/ trang</span>
              <span class="ms-2">Tổng số: {{ totalItems }} lịch học</span>
            </div>
            <ul class="pagination mb-0">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="currentPage > 1 && changePage(1)">
                  «
                </a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="currentPage > 1 && changePage(currentPage - 1)">
                  ‹
                </a>
              </li>
              
              <!-- Page numbers -->
              <li v-for="page in displayedPages" :key="page" class="page-item" :class="{ active: page === currentPage }">
                <a class="page-link" href="#" @click.prevent="changePage(page)">
                  {{ page }}
                </a>
              </li>
              
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a class="page-link" href="#" @click.prevent="currentPage < totalPages && changePage(currentPage + 1)">
                  ›
                </a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a class="page-link" href="#" @click.prevent="currentPage < totalPages && changePage(totalPages)">
                  »
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <!-- No schedules found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Không tìm thấy lịch học nào.</p>
        </div>
      </div>
    </div>
    
    <!-- Modal thêm/sửa lịch học -->
    <div class="modal fade" id="scheduleModal" tabindex="-1" data-bs-backdrop="static" ref="scheduleModal" :class="{ 'show': showAddForm || editing }" style="z-index: 1050;">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editing ? 'Cập nhật lịch học' : 'Thêm lịch học mới' }}</h5>
            <button type="button" class="btn-close" @click="cancelEdit"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSchedule">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Lớp học <span class="text-danger">*</span></label>
                    <select v-model="form.class_id" class="form-select" required>
                      <option value="">Chọn lớp học</option>
                      <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
                        {{ classItem.code }} - {{ getSubjectName(classItem.subject_id) }}
                      </option>
                    </select>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Phòng học <span class="text-danger">*</span></label>
                    <select v-model="form.classroom_id" class="form-select" required>
                      <option value="">Chọn phòng học</option>
                      <option v-for="classroom in classrooms" :key="classroom.id" :value="classroom.id">
                        {{ classroom.room_number }} - {{ getBuildingName(classroom.building_id) }} ({{ getCampusName(getBuildingCampusId(classroom.building_id)) }})
                      </option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-12">
                  <div class="mb-3">
                    <label class="form-label">Ngày cụ thể <span class="text-danger">*</span></label>
                    <VueFlatpickr
                      v-model="form.specific_date"
                      class="form-control"
                      placeholder="DD/MM/YYYY"
                      :config="flatpickrConfig"
                      required
                    />
                    <div class="form-text text-muted">
                      Ngày trong tuần sẽ được tự động tính từ ngày cụ thể
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Thời gian bắt đầu <span class="text-danger">*</span></label>
                    <input 
                      type="time" 
                      v-model="form.start_time" 
                      class="form-control" 
                      required
                    />
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Thời gian kết thúc <span class="text-danger">*</span></label>
                    <input 
                      type="time" 
                      v-model="form.end_time" 
                      class="form-control" 
                      required
                    />
                  </div>
                </div>
              </div>
              
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" @click="cancelEdit">Hủy</button>
                <button type="submit" class="btn btn-primary" :disabled="processing">
                  <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
                  {{ editing ? 'Cập nhật' : 'Thêm mới' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal - Đã tăng z-index lên cao hơn -->
    <div class="modal fade" id="deleteModal" tabindex="-1" data-bs-backdrop="static" ref="deleteModal" style="z-index: 1070;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa lịch học này không?</p>
            <p class="text-danger"><small>Hành động này không thể hoàn tác.</small></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="confirmDeleteSchedule" :disabled="processing">
              <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
              Xóa
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast Notification -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div id="notification" class="toast" role="alert" aria-live="assertive" aria-atomic="true" ref="toastNotification">
        <div class="toast-header" :class="{'bg-success text-white': toastType === 'success', 'bg-danger text-white': toastType === 'error', 'bg-warning text-white': toastType === 'warning'}">
          <strong class="me-auto">{{ toastTitle }}</strong>
          <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
          {{ toastMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { scheduleAPI } from "@/utils/api";
import VueFlatpickr from "vue-flatpickr-component";
import "flatpickr/dist/flatpickr.css";
import Vietnamese from 'flatpickr/dist/l10n/vn.js';
import { Modal, Toast } from 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

export default {
  components: {
    VueFlatpickr
  },
  data() {
    return {
      schedules: [],
      classes: [],
      classrooms: [],
      subjects: [],
      buildings: [],
      campuses: [],
      form: {
        id: null,
        class_id: "",
        classroom_id: "",
        start_time: "",
        end_time: "",
        specific_date: null
      },
      editing: false,
      showAddForm: false,
      currentPage: 1,
      perPage: 10,
      totalItems: 0,
      totalPages: 1,
      filters: {
        class_id: "",
        classroom_id: "",
        specific_date: null
      },
      loading: false,
      processing: false,
      message: "",
      messageType: "success",
      messageTitle: "",
      messageDetails: [],
      // Toast notification
      toastTitle: "Thông báo",
      toastMessage: "",
      toastType: "success",
      flatpickrConfig: {
        dateFormat: "Y-m-d",
        locale: Vietnamese.vn,
        allowInput: true,
        altInput: true,
        altFormat: "d/m/Y",
        parseDate: (datestr, format) => {
          // Xử lý khi người dùng nhập 8 số liên tiếp
          if (/^\d{8}$/.test(datestr)) {
            return new Date(
              datestr.substr(4, 4) + '-' + 
              datestr.substr(2, 2) + '-' + 
              datestr.substr(0, 2)
            );
          }
          return null; // Let flatpickr handle other formats
        }
      },
      scheduleToDeleteId: null,
      confirmingDelete: false
    };
  },
  computed: {
    displayedPages() {
      const pages = [];
      const maxPagesToShow = 5;
      
      let startPage = Math.max(1, this.currentPage - Math.floor(maxPagesToShow / 2));
      let endPage = startPage + maxPagesToShow - 1;
      
      if (endPage > this.totalPages) {
        endPage = this.totalPages;
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      
      return pages;
    },
    hasDetails() {
      return Array.isArray(this.messageDetails) && this.messageDetails.length > 0;
    },
    getAlertIcon() {
      const iconMap = {
        success: "bi bi-check-circle-fill text-success",
        danger: "bi bi-exclamation-triangle-fill text-danger",
        warning: "bi bi-exclamation-circle-fill text-warning",
        info: "bi bi-info-circle-fill text-info"
      };
      return iconMap[this.messageType] || "bi bi-info-circle-fill text-info";
    }
  },
  methods: {
    async fetchSchedules() {
      try {
        this.loading = true;
        const activeFilters = {};
        for (const key in this.filters) {
          if (this.filters[key]) {
            activeFilters[key] = this.filters[key];
          }
        }

        const response = await scheduleAPI.getSchedules(
          this.currentPage,
          this.perPage,
          activeFilters
        );
        
        this.schedules = response.data.items;
        this.totalItems = response.data.pagination.total;
        this.totalPages = response.data.pagination.pages;
      } catch (error) {
        console.error("Lỗi khi tải lịch học:", error);
        this.showMessage("Không thể tải danh sách lịch học", "danger");
      } finally {
        this.loading = false;
      }
    },
    
    async fetchMasterData() {
      try {
        this.loading = true;
        const classesResponse = await scheduleAPI.getClasses();
        this.classes = classesResponse.data.items;
        
        const classroomsResponse = await scheduleAPI.getClassrooms();
        this.classrooms = classroomsResponse.data.items;
        
        const subjectsResponse = await scheduleAPI.getSubjects();
        this.subjects = subjectsResponse.data.items;
        
        const buildingsResponse = await scheduleAPI.getBuildings();
        this.buildings = buildingsResponse.data.items;
        
        const campusesResponse = await scheduleAPI.getCampuses();
        this.campuses = campusesResponse.data.items;
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu:", error);
        this.showMessage("Không thể tải dữ liệu cần thiết", "danger");
      } finally {
        this.loading = false;
      }
    },
    
    async saveSchedule() {
      try {
        this.processing = true;
        const scheduleData = { ...this.form };
        
        // Đảm bảo luôn có specific_date
        if (!scheduleData.specific_date) {
          this.showMessage("Ngày cụ thể là bắt buộc", "danger");
          this.processing = false;
          return;
        }
        
        if (this.editing) {
          await scheduleAPI.updateSchedule(this.form.id, scheduleData);
          this.showMessage("Cập nhật lịch học thành công", "success");
        } else {
          await scheduleAPI.createSchedule(scheduleData);
          this.showMessage("Thêm lịch học mới thành công", "success");
        }
        
        this.fetchSchedules();
        this.cancelEdit();
      } catch (error) {
        console.error("Lỗi khi lưu lịch học:", error);
        
        // Xử lý chi tiết các loại lỗi xung đột lịch học
        if (error.response?.data) {
          const errorData = error.response.data;
          let errorMessage = errorData.error || "Lỗi khi lưu lịch học";
          
          // Hiển thị thông tin chi tiết nếu có
          if (errorData.detail) {
            errorMessage += ": " + errorData.detail;
          }
          
          this.showMessage(errorMessage, "danger");
        } else {
          this.showMessage("Lỗi khi lưu lịch học", "danger");
        }
      } finally {
        this.processing = false;
      }
    },
    
    editSchedule(schedule) {
      this.form = { 
        id: schedule.id,
        class_id: schedule.class_id,
        classroom_id: schedule.classroom_id,
        start_time: schedule.start_time,
        end_time: schedule.end_time,
        specific_date: schedule.specific_date
      };
      this.editing = true;
      this.showAddForm = false;
    },
    
    async deleteSchedule(id) {
      // Lưu ID lịch học cần xóa vào state
      this.scheduleToDeleteId = id;
      this.confirmingDelete = true;
      
      // Hiển thị modal xác nhận xóa
      const modalElement = this.$refs.deleteModal;
      if (modalElement) {
        const deleteModalInstance = new Modal(modalElement);
        deleteModalInstance.show();
      } else {
        // Fallback nếu không tìm thấy modal element
        if (confirm("Bạn có chắc chắn muốn xóa lịch học này không?")) {
          this.confirmDeleteSchedule();
        }
      }
    },
    
    async confirmDeleteSchedule() {
      try {
        this.processing = true;
        await scheduleAPI.deleteSchedule(this.scheduleToDeleteId);
        
        // Đóng modal xác nhận
        const modalElement = this.$refs.deleteModal;
        if (modalElement) {
          const modalInstances = Modal.getInstance(modalElement);
          if (modalInstances) {
            modalInstances.hide();
          }
        }
        
        this.showMessage("Xóa lịch học thành công", "success");
        this.fetchSchedules();
      } catch (error) {
        console.error("Lỗi khi xóa lịch học:", error);
        this.showMessage("Không thể xóa lịch học", "danger");
      } finally {
        this.processing = false;
        this.confirmingDelete = false;
      }
    },
    
    cancelEdit() {
      this.resetForm();
      this.editing = false;
      this.showAddForm = false;
    },
    
    resetForm() {
      this.form = {
        id: null,
        class_id: "",
        classroom_id: "",
        start_time: "",
        end_time: "",
        specific_date: null
      };
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        this.fetchSchedules();
      }
    },
    
    getClassName(classId) {
      const classItem = this.classes.find(c => c.id === classId);
      return classItem ? classItem.code : `Lớp #${classId}`;
    },
    
    getClassroomName(classroomId) {
      const classroom = this.classrooms.find(c => c.id === classroomId);
      return classroom ? classroom.room_number : `Phòng #${classroomId}`;
    },
    
    getSubjectName(subjectId) {
      const subject = this.subjects.find(s => s.id === subjectId);
      return subject ? subject.name : '';
    },
    
    getBuildingName(buildingId) {
      const building = this.buildings.find(b => b.id === buildingId);
      return building ? building.name : '';
    },
    
    getCampusName(campusId) {
      const campus = this.campuses.find(c => c.id === campusId);
      return campus ? campus.name : '';
    },
    
    getBuildingCampusId(buildingId) {
      const building = this.buildings.find(b => b.id === buildingId);
      return building ? building.campus_id : null;
    },
    
    getDayOfWeekText(day) {
      const dayMap = {
        'MON': 'Thứ 2',
        'TUE': 'Thứ 3',
        'WED': 'Thứ 4',
        'THU': 'Thứ 5',
        'FRI': 'Thứ 6',
        'SAT': 'Thứ 7',
        'SUN': 'Chủ nhật'
      };
      return dayMap[day] || day;
    },
    
    showMessage(text, type = 'success', details = null) {
      // Cập nhật thông tin cho toast notification
      this.toastTitle = "Thông báo";
      this.toastMessage = text;
      this.toastType = type === "danger" ? "error" : type;
      
      // Vẫn giữ lại cách hiển thị alert hiện tại cho trường hợp có chi tiết phức tạp
      if (details || (text && text.includes(":"))) {
        this.message = text;
        this.messageType = type;
        this.messageDetails = [];
        
        // Xử lý khi message có dạng "Tiêu đề: Chi tiết"
        if (text && text.includes(":")) {
          const parts = text.split(":");
          this.messageTitle = parts[0].trim();
          
          if (parts.length > 1) {
            // Kiểm tra nếu chi tiết chứa từ khóa về các loại xung đột
            const detailText = parts.slice(1).join(":").trim();
            
            if (detailText.includes("sinh viên") || detailText.includes("giáo viên") || 
                detailText.includes("lớp học") || detailText.includes("phòng học")) {
              
              // Parse các thông tin xung đột
              this.parseConflictDetails(detailText);
            } else {
              // Nếu không phải dạng xung đột đặc biệt, hiển thị nguyên text
              this.messageDetails = [detailText];
            }
          }
        } else {
          this.messageTitle = text;
        }
        
        // Nếu có thông tin chi tiết bổ sung được cung cấp
        if (details) {
          if (Array.isArray(details)) {
            this.messageDetails = [...this.messageDetails, ...details];
          } else {
            this.messageDetails.push(details);
          }
        }
        
        // Tăng thời gian hiển thị nếu có chi tiết
        const displayTime = this.messageDetails.length > 0 ? 6000 : 3000;
        
        setTimeout(() => {
          this.message = '';
          this.messageTitle = '';
          this.messageDetails = [];
        }, displayTime);
      } else {
        // Nếu là thông báo đơn giản, chỉ hiển thị toast
        this.message = '';
        
        // Hiển thị Toast notification
        const toastEl = this.$refs.toastNotification;
        if (toastEl) {
          const toast = new Toast(toastEl);
          toast.show();
        }
      }
    },
    
    parseConflictDetails(detailText) {
      // Xử lý các dạng thông báo lỗi phổ biến
      if (detailText.includes("sinh viên có lịch trùng")) {
        this.messageDetails.push("Có sinh viên đã được xếp lịch học vào cùng thời điểm này");
        this.messageDetails.push(detailText);
        this.messageDetails.push("Vui lòng chọn thời điểm khác hoặc thay đổi danh sách sinh viên của lớp");
      }
      else if (detailText.includes("giáo viên có lịch trùng")) {
        this.messageDetails.push("Có giáo viên đã được phân công dạy vào cùng thời điểm này");
        this.messageDetails.push(detailText);
        this.messageDetails.push("Vui lòng chọn thời điểm khác hoặc phân công giáo viên khác");
      }
      else {
        this.messageDetails.push(detailText);
      }
    },
    
    changePerPage() {
      this.currentPage = 1;
      this.fetchSchedules();
    }
  },
  mounted() {
    this.fetchMasterData();
    this.fetchSchedules();
  }
};
</script>

<style scoped>
/* Add modal styles for when Bootstrap JS is not available */
.modal {
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050;
}

/* Hide scrollbar on body when modal is shown */
:global(body.modal-open) {
  overflow: hidden;
}
</style>

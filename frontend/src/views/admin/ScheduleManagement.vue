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
          {{ message }}
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
                {{ classroom.room_number }} - {{ getBuildingName(classroom.building_id) }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Ngày học</label>
            <div class="d-flex">
              <select v-model="filters.day_of_week" class="form-select flex-grow-1">
                <option value="">Tất cả các ngày</option>
                <option value="MON">Thứ 2</option>
                <option value="TUE">Thứ 3</option>
                <option value="WED">Thứ 4</option>
                <option value="THU">Thứ 5</option>
                <option value="FRI">Thứ 6</option>
                <option value="SAT">Thứ 7</option>
                <option value="SUN">Chủ nhật</option>
              </select>
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
    <div class="modal fade" id="scheduleModal" tabindex="-1" ref="scheduleModal" :class="{ 'show d-block': showAddForm || editing }" style="z-index: 1060;">
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
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Ngày trong tuần <span class="text-danger">*</span></label>
                    <select v-model="form.day_of_week" class="form-select" required>
                      <option value="">Chọn ngày</option>
                      <option value="MON">Thứ 2</option>
                      <option value="TUE">Thứ 3</option>
                      <option value="WED">Thứ 4</option>
                      <option value="THU">Thứ 5</option>
                      <option value="FRI">Thứ 6</option>
                      <option value="SAT">Thứ 7</option>
                      <option value="SUN">Chủ nhật</option>
                    </select>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Ngày cụ thể (tùy chọn)</label>
                    <input 
                      type="date" 
                      v-model="form.specific_date" 
                      class="form-control"
                    />
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
    
    <!-- Modal backdrop -->
    <div class="modal-backdrop fade show" v-if="showAddForm || editing" @click="cancelEdit" style="z-index: 1050;"></div>
  </div>
</template>

<script>
import { scheduleAPI } from "@/utils/api";

export default {
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
        day_of_week: "",
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
        day_of_week: ""
      },
      loading: false,
      processing: false,
      message: "",
      messageType: "success"
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
        
        if (!scheduleData.specific_date) {
          scheduleData.specific_date = null;
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
        this.showMessage(error.response?.data?.error || "Lỗi khi lưu lịch học", "danger");
      } finally {
        this.processing = false;
      }
    },
    
    editSchedule(schedule) {
      this.form = { 
        id: schedule.id,
        class_id: schedule.class_id,
        classroom_id: schedule.classroom_id,
        day_of_week: schedule.day_of_week,
        start_time: schedule.start_time,
        end_time: schedule.end_time,
        specific_date: schedule.specific_date
      };
      this.editing = true;
      this.showAddForm = false;
    },
    
    async deleteSchedule(id) {
      if (confirm("Bạn có chắc muốn xóa lịch học này?")) {
        try {
          this.processing = true;
          await scheduleAPI.deleteSchedule(id);
          this.showMessage("Xóa lịch học thành công", "success");
          this.fetchSchedules();
        } catch (error) {
          console.error("Lỗi khi xóa lịch học:", error);
          this.showMessage("Không thể xóa lịch học", "danger");
        } finally {
          this.processing = false;
        }
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
        day_of_week: "",
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
    
    showMessage(text, type = 'success') {
      this.message = text;
      this.messageType = type;
      
      setTimeout(() => {
        this.message = '';
      }, 3000);
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
  
<template>
  <div class="classroom-management container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <button @click="goBackToBuildings" class="btn btn-outline-secondary btn-sm me-2">
          <i class="bi bi-arrow-left"></i> Quay lại
        </button>
        <h5 class="d-inline mb-0">Danh sách phòng học thuộc {{ buildingName }}</h5>
      </div>
      <button @click="openCreateModal" class="btn btn-primary btn-sm">
        <i class="bi bi-plus-circle me-1"></i>Thêm phòng học mới
      </button>
    </div>
    
    <!-- Search and filter -->
    <div class="row mb-3">
      <div class="col-md-8">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            class="form-control" 
            placeholder="Tìm kiếm theo mã phòng..." 
            v-model="searchQuery"
            @input="onSearchInput"
          >
          <button class="btn btn-outline-secondary" type="button" @click="fetchClassrooms">
            <i class="bi bi-search"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Loading spinner -->
    <div v-if="loading" class="text-center my-3">
      <div class="spinner-border spinner-border-sm text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Đang tải dữ liệu...</p>
    </div>
    
    <!-- Classrooms table -->
    <div v-else-if="classrooms.length" class="table-responsive">
      <table class="table table-striped table-hover align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">#</th>
            <th scope="col">Mã phòng học</th>
            <th scope="col">Sức chứa</th>
            <th scope="col">Cơ sở vật chất</th>
            <th scope="col">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(classroom, index) in classrooms" :key="classroom.id">
            <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
            <td>{{ classroom.room_number }}</td>
            <td>{{ classroom.capacity }} người</td>
            <td>{{ classroom.facilities || 'Không có' }}</td>
            <td>
              <div class="btn-group btn-group-sm">
                <button @click="openEditModal(classroom)" class="btn btn-outline-primary" title="Sửa">
                  <i class="bi bi-pencil-square"></i>
                </button>
                <button @click="confirmDelete(classroom)" class="btn btn-outline-danger" title="Xóa">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Pagination -->
      <Pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total-items="totalItems"
        :total-pages="totalPages"
        item-label="phòng học"
        @page-change="changePage"
        @page-size-change="changePageSize"
      />
    </div>
    
    <!-- No classrooms found -->
    <div v-else class="text-center my-3">
      <i class="bi bi-emoji-frown fs-3 text-muted"></i>
      <p class="mt-2">Không tìm thấy phòng học nào.</p>
    </div>
    
    <!-- Modal thêm/sửa phòng học -->
    <div class="modal fade" id="classroomModal" tabindex="-1" data-bs-backdrop="static" ref="classroomModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Cập nhật phòng học' : 'Thêm phòng học mới' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="isEditing ? updateClassroom() : createClassroom()">
              <div class="mb-3">
                <label class="form-label">Mã phòng học <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentClassroom.room_number" required maxlength="50">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Sức chứa <span class="text-danger">*</span></label>
                <input type="number" class="form-control" v-model="currentClassroom.capacity" required min="1" max="500">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Cơ sở vật chất</label>
                <textarea class="form-control" v-model="currentClassroom.facilities" rows="3" maxlength="500"></textarea>
              </div>
              
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Hủy</button>
                <button type="submit" class="btn btn-primary" :disabled="processing">
                  <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
                  {{ isEditing ? 'Cập nhật' : 'Thêm mới' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteClassroomModal" tabindex="-1" data-bs-backdrop="static" ref="deleteClassroomModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa phòng học <strong>{{ deleteClassroomNumber }}</strong> không?</p>
            <p class="text-danger"><small>Hành động này không thể hoàn tác.</small></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteClassroom" :disabled="processing">
              <span v-if="processing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
              Xóa
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast Notifications -->
    <div class="toast-container">
      <div v-for="notification in notifications" :key="notification.id" 
           class="toast show" :class="'bg-' + notification.type">
        <div class="toast-header">
          <strong class="me-auto">{{ notification.title }}</strong>
          <button type="button" class="btn-close" 
                  @click="notifications = notifications.filter(n => n.id !== notification.id)"></button>
        </div>
        <div class="toast-body text-white">
          {{ notification.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue';
import api from '@/utils/api';
import { Modal } from 'bootstrap';
import Pagination from '@/components/Pagination.vue';
import { debounce } from '@/utils/debounce';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'ClassroomManagement',
  components: {
    Pagination
  },
  props: {
    buildingId: {
      type: [Number, String],
      required: false
    }
  },
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    
    // Get buildingId from either props or route params
    const currentBuildingId = computed(() => {
      return props.buildingId || parseInt(route.params.buildingId);
    });
    
    // Get buildingName from route query
    const buildingName = ref(route.query.buildingName || 'Tòa nhà');
    
    // Navigation
    const goBackToBuildings = () => {
      router.go(-1); // Go back to previous page
    };
    
    // Create a toast notification system
    const notifications = ref([]);
    const showNotification = (title, message, type) => {
      const id = Date.now();
      notifications.value.push({ id, title, message, type });
      
      // Auto remove after 5 seconds
      setTimeout(() => {
        const index = notifications.value.findIndex(n => n.id === id);
        if (index !== -1) {
          notifications.value.splice(index, 1);
        }
      }, 5000);
    };
    
    // State
    const classrooms = ref([]);
    const searchQuery = ref('');
    const loading = ref(true);
    const processing = ref(false);
    const isEditing = ref(false);
    
    // Pagination state
    const currentPage = ref(1);
    const pageSize = ref(5);
    const totalItems = ref(0);
    const totalPages = ref(0);
    
    // Current classroom being edited
    const currentClassroom = reactive({
      id: null,
      room_number: '',
      capacity: 30,
      facilities: '',
      building_id: currentBuildingId.value
    });
    
    // Delete confirmation
    const deleteClassroomId = ref(null);
    const deleteClassroomNumber = ref('');
    
    // Mounted lifecycle hook
    onMounted(() => {
      // Clean up any modal artifacts that might be left from previous views
      const modalBackdrops = document.querySelectorAll('.modal-backdrop');
      modalBackdrops.forEach(backdrop => {
        backdrop.classList.remove('show');
        backdrop.remove();
      });
      
      // Ensure body doesn't have modal classes
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
      
      if (currentBuildingId.value) {
        fetchClassrooms();
      }
    });
    
    // Methods
    const fetchClassrooms = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        
        // Ensure building_id is valid
        if (!currentBuildingId.value) {
          showNotification('Lỗi', 'ID tòa nhà không hợp lệ', 'error');
          loading.value = false;
          return;
        }
        
        console.log("Fetching classrooms with building_id:", currentBuildingId.value);
        
        const response = await api.get('/classrooms', {
          params: {
            page: currentPage.value,
            per_page: pageSize.value,
            query: searchQuery.value || undefined,
            building_id: currentBuildingId.value
          },
          headers: {
            'Authorization': token
          }
        });
        
        // Update with paginated data
        if (response.data && response.data.items) {
          classrooms.value = response.data.items;
          
          // Update pagination info
          totalItems.value = response.data.pagination.total;
          totalPages.value = response.data.pagination.pages;
        } else {
          classrooms.value = response.data;
        }
      } catch (error) {
        console.error('Error fetching classrooms:', error);
        classrooms.value = []; // Reset classrooms to empty array
        
        // Extract error message from response if available
        let errorMessage = 'Không thể tải danh sách phòng học';
        if (error.response && error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        }
        
        showNotification('Lỗi', errorMessage, 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const onSearchInput = () => {
      debouncedSearch();
    };
    
    const debouncedSearch = debounce(() => {
      // Reset to first page when searching
      currentPage.value = 1;
      fetchClassrooms();
    }, 500);
    
    const changePage = (page) => {
      currentPage.value = page;
      fetchClassrooms();
    };
    
    const changePageSize = (size) => {
      pageSize.value = size;
      currentPage.value = 1; // Reset to first page
      fetchClassrooms();
    };
    
    const resetForm = () => {
      currentClassroom.id = null;
      currentClassroom.room_number = '';
      currentClassroom.capacity = 30;
      currentClassroom.facilities = '';
      currentClassroom.building_id = currentBuildingId.value;
    };
    
    const openCreateModal = () => {
      resetForm();
      isEditing.value = false;
      
      const modalElement = document.getElementById('classroomModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const openEditModal = (classroom) => {
      currentClassroom.id = classroom.id;
      currentClassroom.room_number = classroom.room_number;
      currentClassroom.capacity = classroom.capacity;
      currentClassroom.facilities = classroom.facilities || '';
      currentClassroom.building_id = currentBuildingId.value;
      
      isEditing.value = true;
      
      const modalElement = document.getElementById('classroomModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const createClassroom = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.post('/classrooms', currentClassroom, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchClassrooms();
        
        const modalElement = document.getElementById('classroomModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Thêm phòng học mới thành công', 'success');
      } catch (error) {
        console.error('Error creating classroom:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể thêm phòng học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const updateClassroom = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.put(`/classrooms/${currentClassroom.id}`, currentClassroom, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchClassrooms();
        
        const modalElement = document.getElementById('classroomModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Cập nhật phòng học thành công', 'success');
      } catch (error) {
        console.error('Error updating classroom:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể cập nhật phòng học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const confirmDelete = (classroom) => {
      deleteClassroomId.value = classroom.id;
      deleteClassroomNumber.value = classroom.room_number;
      
      const modalElement = document.getElementById('deleteClassroomModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const deleteClassroom = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.delete(`/classrooms/${deleteClassroomId.value}`, {
          headers: {
            'Authorization': token
          }
        });
        
        await fetchClassrooms();
        
        const modalElement = document.getElementById('deleteClassroomModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Xóa phòng học thành công', 'success');
      } catch (error) {
        console.error('Error deleting classroom:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể xóa phòng học', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    return {
      buildingName,
      classrooms,
      searchQuery,
      loading,
      processing,
      isEditing,
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      currentClassroom,
      deleteClassroomId,
      deleteClassroomNumber,
      notifications,
      fetchClassrooms,
      onSearchInput,
      changePage,
      changePageSize,
      openCreateModal,
      openEditModal,
      createClassroom,
      updateClassroom,
      confirmDelete,
      deleteClassroom,
      goBackToBuildings
    };
  }
}
</script>

<style scoped>
.classroom-management {
  padding: 20px;
}

/* Toast notifications */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
}

.toast {
  margin-bottom: 10px;
}
</style> 
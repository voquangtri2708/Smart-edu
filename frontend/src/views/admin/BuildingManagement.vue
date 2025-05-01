<template>
  <div class="building-management container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <button @click="goBackToCampuses" class="btn btn-outline-secondary btn-sm me-2">
          <i class="bi bi-arrow-left"></i> Quay lại
        </button>
        <h5 class="d-inline mb-0">Danh sách tòa nhà thuộc {{ campusName }}</h5>
      </div>
      <button @click="openCreateModal" class="btn btn-primary btn-sm">
        <i class="bi bi-plus-circle me-1"></i>Thêm tòa nhà mới
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
            placeholder="Tìm kiếm theo tên tòa nhà..." 
            v-model="searchQuery"
            @input="onSearchInput"
          >
          <button class="btn btn-outline-secondary" type="button" @click="fetchBuildings">
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
    
    <!-- Buildings table -->
    <div v-else-if="buildings.length" class="table-responsive">
      <table class="table table-striped table-hover align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">#</th>
            <th scope="col">Tên tòa nhà</th>
            <th scope="col">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(building, index) in buildings" :key="building.id">
            <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
            <td>{{ building.name }}</td>
            <td>
              <div class="btn-group btn-group-sm">
                <button @click="openEditModal(building)" class="btn btn-outline-primary" title="Sửa">
                  <i class="bi bi-pencil-square"></i>
                </button>
                <button @click="confirmDelete(building)" class="btn btn-outline-danger" title="Xóa">
                  <i class="bi bi-trash"></i>
                </button>
                <button @click="manageClassroomsForBuilding(building)" class="btn btn-outline-success" title="Quản lý phòng học">
                  <i class="bi bi-door-open"></i>
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
        item-label="tòa nhà"
        @page-change="changePage"
        @page-size-change="changePageSize"
      />
    </div>
    
    <!-- No buildings found -->
    <div v-else class="text-center my-3">
      <i class="bi bi-emoji-frown fs-3 text-muted"></i>
      <p class="mt-2">Không tìm thấy tòa nhà nào.</p>
    </div>
    
    <!-- Modal thêm/sửa tòa nhà -->
    <div class="modal fade" id="buildingModal" tabindex="-1" data-bs-backdrop="static" ref="buildingModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Cập nhật tòa nhà' : 'Thêm tòa nhà mới' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="isEditing ? updateBuilding() : createBuilding()">
              <div class="mb-3">
                <label class="form-label">Tên tòa nhà <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentBuilding.name" required maxlength="255">
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
    <div class="modal fade" id="deleteBuildingModal" tabindex="-1" data-bs-backdrop="static" ref="deleteBuildingModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa tòa nhà <strong>{{ deleteBuildingName }}</strong> không?</p>
            <p class="text-danger"><small>Hành động này không thể hoàn tác.</small></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteBuilding" :disabled="processing">
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
import axios from 'axios';
import { Modal } from 'bootstrap';
import Pagination from '@/components/Pagination.vue';
import { debounce } from '@/utils/debounce';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'BuildingManagement',
  components: {
    Pagination
  },
  props: {
    campusId: {
      type: [Number, String],
      required: false
    },
    campusName: {
      type: String,
      required: false
    }
  },
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    
    // Get campusId from either props or route params
    const currentCampusId = computed(() => {
      return props.campusId || parseInt(route.params.campusId);
    });
    
    // Get campusName from route query or props
    const campusName = ref(props.campusName || route.query.campusName || 'Cơ sở');
    
    // Navigation
    const goBackToCampuses = () => {
      // Remove any existing modal backdrops before navigation
      const modalBackdrops = document.querySelectorAll('.modal-backdrop');
      modalBackdrops.forEach(backdrop => {
        backdrop.classList.remove('show');
        backdrop.remove();
      });
      
      // Ensure body doesn't have modal classes
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
      
      // Navigate back to campuses
      router.push({ name: 'admin-campus-management' });
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
    const buildings = ref([]);
    const searchQuery = ref('');
    const loading = ref(true);
    const processing = ref(false);
    const isEditing = ref(false);
    
    // Pagination state
    const currentPage = ref(1);
    const pageSize = ref(5);
    const totalItems = ref(0);
    const totalPages = ref(0);
    
    // Current building being edited
    const currentBuilding = reactive({
      id: null,
      name: '',
      campus_id: currentCampusId.value
    });
    
    // Delete confirmation
    const deleteBuildingId = ref(null);
    const deleteBuildingName = ref('');
    
    // Clean up modal artifacts on mount
    onMounted(() => {
      // Clean up any modal artifacts that might be left
      const modalBackdrops = document.querySelectorAll('.modal-backdrop');
      modalBackdrops.forEach(backdrop => {
        backdrop.classList.remove('show');
        backdrop.remove();
      });
      
      // Ensure body doesn't have modal classes
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
      
      if (currentCampusId.value) {
        fetchBuildings();
      }
    });
    
    // Methods
    const fetchBuildings = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        
        // Ensure campus_id is a valid number
        if (!currentCampusId.value) {
          showNotification('Lỗi', 'ID cơ sở không hợp lệ', 'error');
          loading.value = false;
          return;
        }
        
        console.log("Fetching buildings with campus_id:", currentCampusId.value);
        
        const response = await axios.get('http://localhost:5000/api/buildings', {
          params: {
            page: currentPage.value,
            per_page: pageSize.value,
            query: searchQuery.value || undefined,
            campus_id: currentCampusId.value
          },
          headers: {
            'Authorization': token
          }
        });
        
        // Update with paginated data
        if (response.data && response.data.items) {
          buildings.value = response.data.items;
          
          // Update pagination info
          totalItems.value = response.data.pagination.total;
          totalPages.value = response.data.pagination.pages;
        } else {
          buildings.value = response.data;
        }
      } catch (error) {
        console.error('Error fetching buildings:', error);
        buildings.value = []; // Reset buildings to empty array
        
        // Extract error message from response if available
        let errorMessage = 'Không thể tải danh sách tòa nhà';
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
      fetchBuildings();
    }, 500);
    
    const changePage = (page) => {
      currentPage.value = page;
      fetchBuildings();
    };
    
    const changePageSize = (size) => {
      pageSize.value = size;
      currentPage.value = 1; // Reset to first page
      fetchBuildings();
    };
    
    const resetForm = () => {
      currentBuilding.id = null;
      currentBuilding.name = '';
      currentBuilding.campus_id = currentCampusId.value;
    };
    
    const openCreateModal = () => {
      resetForm();
      isEditing.value = false;
      
      const modalElement = document.getElementById('buildingModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const openEditModal = (building) => {
      currentBuilding.id = building.id;
      currentBuilding.name = building.name;
      currentBuilding.campus_id = currentCampusId.value;
      
      isEditing.value = true;
      
      const modalElement = document.getElementById('buildingModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const createBuilding = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.post('http://localhost:5000/api/buildings', currentBuilding, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchBuildings();
        
        const modalElement = document.getElementById('buildingModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Thêm tòa nhà mới thành công', 'success');
      } catch (error) {
        console.error('Error creating building:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể thêm tòa nhà', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const updateBuilding = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.put(`http://localhost:5000/api/buildings/${currentBuilding.id}`, currentBuilding, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchBuildings();
        
        const modalElement = document.getElementById('buildingModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Cập nhật tòa nhà thành công', 'success');
      } catch (error) {
        console.error('Error updating building:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể cập nhật tòa nhà', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const confirmDelete = (building) => {
      deleteBuildingId.value = building.id;
      deleteBuildingName.value = building.name;
      
      const modalElement = document.getElementById('deleteBuildingModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const deleteBuilding = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await axios.delete(`http://localhost:5000/api/buildings/${deleteBuildingId.value}`, {
          headers: {
            'Authorization': token
          }
        });
        
        await fetchBuildings();
        
        const modalElement = document.getElementById('deleteBuildingModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Xóa tòa nhà thành công', 'success');
      } catch (error) {
        console.error('Error deleting building:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể xóa tòa nhà', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const manageClassroomsForBuilding = (building) => {
      // Remove any existing modal backdrops before navigation
      const modalBackdrops = document.querySelectorAll('.modal-backdrop');
      modalBackdrops.forEach(backdrop => {
        backdrop.classList.remove('show');
        backdrop.remove();
      });
      
      // Ensure body doesn't have modal classes
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
      
      // Then navigate to the classroom management page
      router.push({
        name: 'classroom-management',
        params: { buildingId: building.id },
        query: { buildingName: building.name }
      });
    };
    
    return {
      campusName,
      buildings,
      searchQuery,
      loading,
      processing,
      isEditing,
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      currentBuilding,
      deleteBuildingId,
      deleteBuildingName,
      notifications,
      fetchBuildings,
      onSearchInput,
      changePage,
      changePageSize,
      openCreateModal,
      openEditModal,
      createBuilding,
      updateBuilding,
      confirmDelete,
      deleteBuilding,
      manageClassroomsForBuilding,
      goBackToCampuses
    };
  }
}
</script>

<style scoped>
.building-management {
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
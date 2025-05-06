<template>
  <div class="facility-management">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Quản Lý Cơ Sở</h4>
        <button @click="openCreateModal" class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i>Thêm Cơ Sở Mới
        </button>
      </div>
      
      <div class="card-body">
        <!-- Hiển thị thông báo -->
        <div v-if="message" :class="'alert alert-' + messageType" role="alert">
          {{ message }}
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
                placeholder="Tìm kiếm theo tên hoặc địa chỉ..." 
                v-model="searchQuery"
                @input="onSearchInput"
              >
              <button class="btn btn-outline-secondary" type="button" @click="fetchCampuses">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          
          <div class="col-md-2">
            <select class="form-select" v-model="sortBy" @change="sortCampuses">
              <option value="name">Sắp xếp theo tên</option>
              <option value="address">Sắp xếp theo địa chỉ</option>
            </select>
          </div>
          
          <div class="col-md-2">
            <select class="form-select" v-model="sortOrder" @change="sortCampuses">
              <option value="asc">Tăng dần</option>
              <option value="desc">Giảm dần</option>
            </select>
          </div>
        </div>
        
        <!-- Loading spinner -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Đang tải dữ liệu...</p>
        </div>
        
        <!-- Campuses table -->
        <div v-else-if="campuses.length" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Tên cơ sở</th>
                <th scope="col">Địa chỉ</th>
                <th scope="col">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(campus, index) in campuses" :key="campus.id">
                <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                <td>{{ campus.name }}</td>
                <td>{{ campus.address }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button @click="openEditModal(campus)" class="btn btn-outline-primary" title="Sửa">
                      <i class="bi bi-pencil-square"></i>
                    </button>
                    <button @click="confirmDelete(campus)" class="btn btn-outline-danger" title="Xóa">
                      <i class="bi bi-trash"></i>
                    </button>
                    <button @click="manageBuildingsForCampus(campus)" class="btn btn-outline-success" title="Quản lý tòa nhà">
                      <i class="bi bi-building"></i>
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
            item-label="cơ sở"
            @page-change="changePage"
            @page-size-change="changePageSize"
          />
        </div>
        
        <!-- No campuses found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Không tìm thấy cơ sở nào.</p>
        </div>
      </div>
    </div>
    
    <!-- Modal thêm/sửa cơ sở -->
    <div class="modal fade" id="campusModal" tabindex="-1" data-bs-backdrop="static" ref="campusModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Cập nhật cơ sở' : 'Thêm cơ sở mới' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="isEditing ? updateCampus() : createCampus()">
              <div class="mb-3">
                <label class="form-label">Tên cơ sở <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentCampus.name" required maxlength="255">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Địa chỉ <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="currentCampus.address" required maxlength="255">
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
    <div class="modal fade" id="deleteModal" tabindex="-1" data-bs-backdrop="static" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xác nhận xóa</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Bạn có chắc chắn muốn xóa cơ sở <strong>{{ deleteCampusName }}</strong> không?</p>
            <p class="text-danger"><small>Hành động này không thể hoàn tác.</small></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
            <button type="button" class="btn btn-danger" @click="deleteCampus" :disabled="processing">
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
        <div class="toast-header" :class="{'bg-success text-white': toastType === 'success', 'bg-danger text-white': toastType === 'error'}">
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
import { ref, reactive, onMounted } from 'vue';
import api from '@/utils/api';
import { Modal, Toast } from 'bootstrap';
import Pagination from '@/components/Pagination.vue';
import { debounce } from '@/utils/debounce';
import { useRouter } from 'vue-router';

export default {
  name: 'FacilityManagement',
  components: {
    Pagination
  },
  setup() {
    const router = useRouter();
    // State
    const campuses = ref([]);
    const searchQuery = ref('');
    const loading = ref(true);
    const processing = ref(false);
    const isEditing = ref(false);
    const message = ref('');
    const messageType = ref('info');
    const sortBy = ref('name');
    const sortOrder = ref('asc');
    
    // Pagination state
    const currentPage = ref(1);
    const pageSize = ref(10);
    const totalItems = ref(0);
    const totalPages = ref(0);
    
    // Current campus being edited
    const currentCampus = reactive({
      id: null,
      name: '',
      address: ''
    });
    
    // Delete confirmation
    const deleteCampusId = ref(null);
    const deleteCampusName = ref('');
    
    // Toast notification
    const toastTitle = ref('');
    const toastMessage = ref('');
    const toastType = ref('success');
    
    // Mounted lifecycle hook
    onMounted(() => {
      // Fetch data
      fetchCampuses();
    });
    
    // Methods
    const fetchCampuses = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        const response = await api.get('/campuses', {
          params: {
            page: currentPage.value,
            per_page: pageSize.value,
            query: searchQuery.value || undefined
          },
          headers: {
            'Authorization': token
          }
        });
        
        // Update with paginated data
        if (response.data && response.data.items) {
          campuses.value = response.data.items;
          
          // Update pagination info
          totalItems.value = response.data.pagination.total;
          totalPages.value = response.data.pagination.pages;
        } else {
          campuses.value = response.data;
        }
        
        sortCampuses(); // Apply default sorting
      } catch (error) {
        console.error('Error fetching campuses:', error);
        showNotification('Lỗi', 'Không thể tải danh sách cơ sở', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const sortCampuses = () => {
      campuses.value.sort((a, b) => {
        let valueA = a[sortBy.value];
        let valueB = b[sortBy.value];
        
        if (typeof valueA === 'string') {
          valueA = valueA.toLowerCase();
          valueB = valueB.toLowerCase();
        }
        
        if (sortOrder.value === 'asc') {
          return valueA > valueB ? 1 : -1;
        } else {
          return valueA < valueB ? 1 : -1;
        }
      });
    };
    
    const onSearchInput = () => {
      debouncedSearch();
    };
    
    const debouncedSearch = debounce(() => {
      // Reset to first page when searching
      currentPage.value = 1;
      fetchCampuses();
    }, 500);
    
    const changePage = (page) => {
      currentPage.value = page;
      fetchCampuses();
    };
    
    const changePageSize = (size) => {
      pageSize.value = size;
      currentPage.value = 1; // Reset to first page
      fetchCampuses();
    };
    
    const resetForm = () => {
      currentCampus.id = null;
      currentCampus.name = '';
      currentCampus.address = '';
    };
    
    const openCreateModal = () => {
      resetForm();
      isEditing.value = false;
      
      const modalElement = document.getElementById('campusModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const openEditModal = (campus) => {
      currentCampus.id = campus.id;
      currentCampus.name = campus.name;
      currentCampus.address = campus.address;
      
      isEditing.value = true;
      
      const modalElement = document.getElementById('campusModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const createCampus = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.post('/campuses', currentCampus, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchCampuses();
        
        const modalElement = document.getElementById('campusModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Thêm cơ sở mới thành công', 'success');
      } catch (error) {
        console.error('Error creating campus:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể thêm cơ sở', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const updateCampus = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.put(`/campuses/${currentCampus.id}`, currentCampus, {
          headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
          }
        });
        
        await fetchCampuses();
        
        const modalElement = document.getElementById('campusModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Cập nhật cơ sở thành công', 'success');
      } catch (error) {
        console.error('Error updating campus:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể cập nhật cơ sở', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const confirmDelete = (campus) => {
      deleteCampusId.value = campus.id;
      deleteCampusName.value = campus.name;
      
      const modalElement = document.getElementById('deleteModal');
      let modalInstance = Modal.getInstance(modalElement);
      
      if (!modalInstance) {
        modalInstance = new Modal(modalElement);
      }
      
      modalInstance.show();
    };
    
    const deleteCampus = async () => {
      processing.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        await api.delete(`/campuses/${deleteCampusId.value}`, {
          headers: {
            'Authorization': token
          }
        });
        
        await fetchCampuses();
        
        const modalElement = document.getElementById('deleteModal');
        const modalInstance = Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
        
        showNotification('Thành công', 'Xóa cơ sở thành công', 'success');
      } catch (error) {
        console.error('Error deleting campus:', error);
        showNotification('Lỗi', error.response?.data?.error || 'Không thể xóa cơ sở', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const manageBuildingsForCampus = (campus) => {
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
      
      // Navigate to the building management route
      router.push({
        name: 'building-management',
        params: { campusId: campus.id },
        query: { campusName: campus.name }
      });
    };
    
    const showNotification = (title, message, type) => {
      toastTitle.value = title;
      toastMessage.value = message;
      toastType.value = type;
      
      // Get the toast element and create instance if needed
      const toastElement = document.getElementById('notification');
      let toastInstance = Toast.getInstance(toastElement);
      
      if (!toastInstance) {
        toastInstance = new Toast(toastElement);
      }
      
      toastInstance.show();
    };
    
    return {
      campuses,
      searchQuery,
      loading,
      processing,
      isEditing,
      message,
      messageType,
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      sortBy,
      sortOrder,
      currentCampus,
      deleteCampusId,
      deleteCampusName,
      toastTitle,
      toastMessage,
      toastType,
      fetchCampuses,
      changePage,
      changePageSize,
      onSearchInput,
      sortCampuses,
      openCreateModal,
      openEditModal,
      createCampus,
      updateCampus,
      confirmDelete,
      deleteCampus,
      manageBuildingsForCampus,
      showNotification
    };
  }
}
</script>

<style scoped>
.facility-management {
  padding: 20px;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  margin-bottom: 20px;
}

.btn-group-sm > .btn {
  margin-right: 2px;
}
</style> 
<template>
  <div class="subject-list">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Danh Sách Môn Học</h4>
      </div>
      
      <div class="card-body">
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
                placeholder="Tìm kiếm theo mã hoặc tên môn học..." 
                v-model="searchQuery"
                @input="handleSearchInput"
              >
              <button class="btn btn-outline-secondary" type="button" @click="fetchSubjects">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" v-model="sortBy" @change="sortSubjects">
              <option value="code">Sắp xếp theo mã</option>
              <option value="name">Sắp xếp theo tên</option>
              <option value="credit">Sắp xếp theo số tín chỉ</option>
            </select>
          </div>
          
          <div class="col-md-3">
            <select class="form-select" v-model="sortOrder" @change="sortSubjects">
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
        
        <!-- Subjects table -->
        <div v-else-if="subjects.length" class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Mã môn học</th>
                <th scope="col">Tên môn học</th>
                <th scope="col">Số tín chỉ</th>
                <th scope="col">Mô tả</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(subject, index) in subjects" :key="subject.id">
                <td>{{ index + 1 }}</td>
                <td>{{ subject.code }}</td>
                <td>{{ subject.name }}</td>
                <td>{{ subject.credit }}</td>
                <td>
                  <span v-if="subject.description" class="d-inline-block text-truncate" style="max-width: 250px;">
                    {{ subject.description }}
                  </span>
                  <span v-else class="text-muted">Không có mô tả</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- No subjects found -->
        <div v-else class="text-center my-5">
          <i class="bi bi-emoji-frown fs-1 text-muted"></i>
          <p class="mt-2">Không tìm thấy môn học nào.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'SubjectList',
  setup() {
    // State
    const subjects = ref([]);
    const searchQuery = ref('');
    const loading = ref(true);
    const sortBy = ref('code');
    const sortOrder = ref('asc');
    
    // Life cycle
    onMounted(async () => {
      await fetchSubjects();
    });
    
    // Methods
    const fetchSubjects = async () => {
      loading.value = true;
      try {
        const token = localStorage.getItem('auth_token');
        const response = await axios.get('http://localhost:5000/api/subjects', {
          headers: {
            'Authorization': token
          }
        });
        subjects.value = response.data;
        sortSubjects(); // Apply default sorting
      } catch (error) {
        console.error('Error fetching subjects:', error);
      } finally {
        loading.value = false;
      }
    };
    
    const handleSearchInput = () => {
      // Implement search filtering logic
      if (searchQuery.value.trim() === '') {
        fetchSubjects();
        return;
      }
      
      const query = searchQuery.value.trim().toLowerCase();
      const filtered = subjects.value.filter(subject => 
        subject.code.toLowerCase().includes(query) || 
        subject.name.toLowerCase().includes(query)
      );
      subjects.value = filtered;
    };
    
    const sortSubjects = () => {
      subjects.value.sort((a, b) => {
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
    
    return {
      subjects,
      searchQuery,
      loading,
      sortBy,
      sortOrder,
      fetchSubjects,
      handleSearchInput,
      sortSubjects
    };
  }
};
</script>

<style scoped>
.subject-list {
  padding: 20px;
}
</style>

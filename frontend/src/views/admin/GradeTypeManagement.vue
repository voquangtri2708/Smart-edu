<template>
  <div class="grade-type-management container mt-4">
    <h2>Quản lý loại điểm</h2>
    <div class="mb-3 d-flex justify-content-between align-items-center">
      <button class="btn btn-primary" @click="openModal()">
        <i class="bi bi-plus-circle me-1"></i> Thêm loại điểm
      </button>
    </div>
    <div class="card">
      <div class="card-body">
        <table class="table table-bordered">
          <thead>
            <tr>
              <th>Tên loại điểm</th>
              <th>Hệ số (%)</th>
              <th>Mô tả</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="gradeType in gradeTypes" :key="gradeType.id">
              <td>{{ gradeType.name }}</td>
              <td>{{ (gradeType.weight * 100).toFixed(0) }}%</td>
              <td>{{ gradeType.description }}</td>
              <td>
                <button class="btn btn-sm btn-warning me-2" @click="openModal(gradeType)"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-danger" @click="confirmDelete(gradeType)"><i class="bi bi-trash"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- Modal -->
    <div class="modal fade" id="gradeTypeModal" tabindex="-1" ref="modalElement">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingGradeType ? 'Cập nhật loại điểm' : 'Thêm loại điểm' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveGradeType">
              <div class="mb-3">
                <label class="form-label">Tên loại điểm</label>
                <input v-model="form.name" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Hệ số (%)</label>
                <input v-model.number="form.weight" type="number" min="1" max="100" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Mô tả</label>
                <input v-model="form.description" class="form-control" />
              </div>
              <button class="btn btn-primary" type="submit">{{ editingGradeType ? 'Cập nhật' : 'Thêm mới' }}</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';
import { Modal } from 'bootstrap';

const gradeTypes = ref([]);
const editingGradeType = ref(null);
const form = ref({ name: '', weight: 1, description: '' });
const modalElement = ref(null);
let modalInstance = null;

const fetchGradeTypes = async () => {
  try {
    const res = await api.get('/grade_types');
    gradeTypes.value = res.data;
  } catch (error) {
    console.error('Error fetching grade types:', error);
  }
};

const openModal = (gradeType = null) => {
  editingGradeType.value = gradeType;
  if (gradeType) {
    form.value = { 
      name: gradeType.name, 
      weight: gradeType.weight * 100, 
      description: gradeType.description 
    };
  } else {
    form.value = { name: '', weight: 1, description: '' };
  }
  
  if (!modalInstance && modalElement.value) {
    modalInstance = new Modal(modalElement.value);
  }
  
  if (modalInstance) {
    modalInstance.show();
  }
};

const saveGradeType = async () => {
  try {
    const payload = { 
      ...form.value, 
      weight: form.value.weight / 100 
    };
    
    if (editingGradeType.value) {
      await api.put(`/grade_types/${editingGradeType.value.id}`, payload);
    } else {
      await api.post('/grade_types', payload);
    }
    
    if (modalInstance) {
      modalInstance.hide();
    }
    await fetchGradeTypes();
  } catch (error) {
    console.error('Error saving grade type:', error);
  }
};

const confirmDelete = async (gradeType) => {
  if (confirm('Bạn có chắc chắn muốn xóa loại điểm này?')) {
    try {
      await api.delete(`/grade_types/${gradeType.id}`);
      await fetchGradeTypes();
    } catch (error) {
      console.error('Error deleting grade type:', error);
    }
  }
};

onMounted(async () => {
  await fetchGradeTypes();
});
</script>
<style scoped>
.grade-type-management { max-width: 900px; }
</style> 
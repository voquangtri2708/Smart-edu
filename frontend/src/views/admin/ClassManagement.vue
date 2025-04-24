<template>
    <div class="container mx-auto p-4 bg-white rounded-xl shadow">
      <h1 class="text-2xl font-bold text-center mb-4">Quản Lý Lớp Học</h1>
  
      <div class="flex justify-center gap-4 mb-6">
        <button :class="['tab-button', activeTab === 'list' ? 'active' : '']" @click="activeTab = 'list'">Danh sách lớp</button>
        <button :class="['tab-button', activeTab === 'students' ? 'active' : '']" @click="activeTab = 'students'" :disabled="!selectedClass">Danh sách sinh viên</button>
      </div>
  
      <!-- Danh sách lớp -->
      <div v-if="activeTab === 'list'">
        <table class="w-full border">
          <thead>
            <tr>
              <th>#</th>
              <th>Mã lớp</th>
              <th>Giáo viên</th>
              <th>Thời gian</th>
              <th>Đề cương</th>
              <th>Sĩ số</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(cls, index) in classes" :key="cls.id">
              <td>{{ index + 1 }}</td>
              <td>{{ cls.code }}</td>
              <td>{{ cls.subject_code }}</td>
              <td>{{ cls.start_date }} - {{ cls.end_date }}</td>
              <td><a href="#">Xem</a></td>
              <td>{{ cls.max_student }}</td>
              <td>
                <button @click="viewStudents(cls)">Xem SV</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- Danh sách sinh viên -->
      <div v-else>
        <h2 class="text-xl font-semibold mb-3">Danh sách sinh viên lớp {{ selectedClass.code }}</h2>
        <table class="w-full border">
          <thead>
            <tr>
              <th>#</th>
              <th>Mã sinh viên</th>
              <th>Họ tên</th>
              <th>Email</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, index) in students" :key="student.id">
              <td>{{ index + 1 }}</td>
              <td>{{ student.code }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  
  const activeTab = ref('list')
  const classes = ref([])
  const selectedClass = ref(null)
  const students = ref([])
  
  const API = 'http://localhost:5000' // Cập nhật nếu backend deploy khác
  
  const fetchClasses = async () => {
    const res = await axios.get(`${API}/classes`)
    classes.value = res.data
  }
  
  const viewStudents = (cls) => {
    selectedClass.value = cls
    activeTab.value = 'students'
  
    // TODO: gọi API thật thay vì mock dữ liệu
    students.value = [
      { id: 1, code: 'SV001', name: 'Nguyễn Văn A', email: 'a@example.com' },
      { id: 2, code: 'SV002', name: 'Trần Thị B', email: 'b@example.com' },
    ]
  }
  
  onMounted(() => {
    fetchClasses()
  })
  </script>
  
  <style scoped>
  .tab-button {
    padding: 10px 20px;
    background: #e2e6ea;
    border-radius: 8px;
    cursor: pointer;
  }
  .tab-button.active {
    background: #0d6efd;
    color: white;
  }
  .tab-button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
  table {
    border-collapse: collapse;
  }
  th, td {
    border: 1px solid #ccc;
    padding: 10px;
  }
  </style>
  
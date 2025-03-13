<template>
    <div class="container">
      <h1>Đánh giá giảng viên</h1>
      <div v-if="teachers.length">
        <div v-for="teacher in teachers" :key="teacher.id" class="teacher-card">
          <h3>{{ teacher.first_name }} {{ teacher.last_name }}</h3>
          <textarea v-model="feedbackContent[teacher.id]" placeholder="Nội dung đánh giá"></textarea>
          <button @click="submitFeedback(teacher.id)">Gửi đánh giá</button>
        </div>
      </div>
      <div v-else>
        <p>Không có giảng viên nào trong lớp của bạn.</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  
  const classId = 1  // Thay thế bằng class_id thực tế của học sinh
  const teachers = ref([])
  const feedbackContent = ref({})
  
  onMounted(async () => {
    const response = await axios.get(`http://localhost:5000/api/class_teachers/${classId}/teachers`)
    teachers.value = response.data
  })
  
  const submitFeedback = async (teacherId) => {
    const content = feedbackContent.value[teacherId]
    if (!content) {
      alert('Vui lòng nhập nội dung đánh giá')
      return
    }
  
    const feedbackData = {
      content,
      student_id: 'student_id',  // Thay thế bằng student_id thực tế
      class_id: classId,
      teacher_id: teacherId
    }
  
    await axios.post('http://localhost:5000/api/teacher_feedbacks', feedbackData)
    alert('Đánh giá đã được gửi')
    feedbackContent.value[teacherId] = ''
  }
  </script>
  
  <style scoped>
  .container {
    max-width: 600px;
    margin: 0 auto;
  }
  
  .teacher-card {
    border: 1px solid #ddd;
    padding: 20px;
    margin-bottom: 20px;
  }
  
  textarea {
    width: 100%;
    height: 100px;
    margin-bottom: 10px;
  }
  
  button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
  }
  
  button:hover {
    background-color: #0056b3;
  }
  </style>
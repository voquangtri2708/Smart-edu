<template>
    <div class="container">
      <h1>Quản lý đánh giá giảng viên</h1>
      <div class="filter">
        <label for="sentiment">Lọc theo sentiment:</label>
        <select v-model="selectedSentiment" @change="fetchFeedbacks">
          <option value="">Tất cả</option>
          <option value="negative">Tiêu cực</option>
          <option value="neutral">Trung lập</option>
          <option value="positive">Tích cực</option>
        </select>
      </div>
      <div v-if="feedbacks.length">
        <div v-for="feedback in feedbacks" :key="feedback.id" class="feedback-card">
          <p><strong>Nội dung:</strong> {{ feedback.content }}</p>
          <p><strong>Sentiment:</strong> {{ feedback.sentiment }}</p>
          <p><strong>Ngày tạo:</strong> {{ feedback.created_at }}</p>
        </div>
      </div>
      <div v-else>
        <p>Không có đánh giá nào.</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  
  const feedbacks = ref([])
  const selectedSentiment = ref('')
  
  const fetchFeedbacks = async () => {
    const response = await axios.get('http://localhost:5000/api/teacher_feedbacks', {
      params: { sentiment: selectedSentiment.value }
    })
    feedbacks.value = response.data
  }
  
  onMounted(fetchFeedbacks)
  </script>
  
  <style scoped>
  .container {
    max-width: 800px;
    margin: 0 auto;
  }
  
  .filter {
    margin-bottom: 20px;
  }
  
  .feedback-card {
    border: 1px solid #ddd;
    padding: 20px;
    margin-bottom: 20px;
  }
  </style>
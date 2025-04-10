<template>
    <div class="schedule-management">
      <h1>Quản lý lịch học</h1>
      
      <!-- Danh sách lịch học -->
      <table>
        <thead>
          <tr>
            <th>STT</th>
            <th>Môn học</th>
            <th>Giáo viên</th>
            <th>Thời gian</th>
            <th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(schedule, index) in schedules" :key="schedule.id">
            <td>{{ index + 1 }}</td>
            <td>{{ schedule.subject }}</td>
            <td>{{ schedule.teacher }}</td>
            <td>{{ schedule.time }}</td>
            <td>
              <button @click="editSchedule(schedule)">Sửa</button>
              <button @click="deleteSchedule(schedule.id)">Xóa</button>
            </td>
          </tr>
        </tbody>
      </table>
  
      <!-- Form tạo hoặc chỉnh sửa lịch -->
      <form @submit.prevent="saveSchedule">
        <h3>{{ editing ? 'Chỉnh sửa lịch' : 'Thêm lịch mới' }}</h3>
        <input v-model="form.subject" placeholder="Tên môn học" required />
        <input v-model="form.teacher" placeholder="Tên giáo viên" required />
        <input v-model="form.time" placeholder="Thời gian (VD: Thứ 2, 14h-16h)" required />
        <button type="submit">{{ editing ? 'Cập nhật' : 'Thêm' }}</button>
        <button type="button" @click="cancelEdit" v-if="editing">Hủy</button>
      </form>
    </div>
  </template>
  
  <script>
  import { scheduleAPI } from "@/utils/api.js";
  
  export default {
    data() {
      return {
        schedules: [],
        form: { id: null, subject: "", teacher: "", time: "" },
        editing: false
      };
    },
    methods: {
      async fetchSchedules() {
        try {
          const { data } = await scheduleAPI.getSchedules();
          this.schedules = data;
        } catch (error) {
          console.error("Lỗi khi tải lịch học:", error);
        }
      },
      async saveSchedule() {
        try {
          if (this.editing) {
            await scheduleAPI.updateSchedule(this.form.id, this.form);
          } else {
            await scheduleAPI.createSchedule(this.form);
          }
          this.fetchSchedules();
          this.resetForm();
        } catch (error) {
          console.error("Lỗi khi lưu lịch học:", error);
        }
      },
      editSchedule(schedule) {
        this.form = { ...schedule };
        this.editing = true;
      },
      async deleteSchedule(id) {
        if (confirm("Bạn có chắc muốn xóa lịch học này?")) {
          try {
            await scheduleAPI.deleteSchedule(id);
            this.fetchSchedules();
          } catch (error) {
            console.error("Lỗi khi xóa lịch học:", error);
          }
        }
      },
      cancelEdit() {
        this.resetForm();
      },
      resetForm() {
        this.form = { id: null, subject: "", teacher: "", time: "" };
        this.editing = false;
      }
    },
    mounted() {
      this.fetchSchedules();
    }
  };
  </script>
  
  <style scoped>
  .schedule-management {
    max-width: 600px;
    margin: auto;
    text-align: center;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
  }
  form {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  button {
    cursor: pointer;
    margin: 5px;
  }
  </style>
  
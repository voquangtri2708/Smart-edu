<template>
    <div class="schedule-container">
      <h2>Quản lý Lịch Học</h2>
      <table>
        <thead>
          <tr>
            <th>Tiết</th>
            <th v-for="(day, index) in days" :key="index">{{ day }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in scheduleData" :key="rowIndex">
            <td>{{ timeSlots[rowIndex] }}</td>
            <td v-for="(cell, cellIndex) in row" :key="cellIndex">
              <div v-if="cell.length">
                <div v-for="(subject, subIndex) in cell" :key="subIndex">
                  <span :class="getSubjectClass(subject.type)">{{ subject.subject }}</span>
                  <button @click="removeSubject(rowIndex, cellIndex, subIndex)">🗑</button>
                </div>
              </div>
              <button @click="addSubject(rowIndex, cellIndex)">➕</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        days: ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"],
        timeSlots: ["Tiết 1-2", "Tiết 3-4", "Tiết 5-6", "Tiết 7-8"],
        scheduleData: [
          [[], [], [], [], [], [], []],
          [[], [], [], [], [], [], []],
          [[], [], [], [], [], [], []],
          [[], [], [], [], [], [], []]
        ],
      };
    },
    methods: {
      addSubject(row, col) {
        const subject = prompt("Nhập môn học:");
        const type = prompt("Nhập loại (Lý Thuyết, Thực Hành, Kiểm Tra):");
  
        if (subject && type) {
          this.scheduleData[row][col].push({ subject, type });
        }
      },
      removeSubject(row, col, index) {
        this.scheduleData[row][col].splice(index, 1);
      },
      getSubjectClass(type) {
        return {
          "Lý Thuyết": "blue",
          "Thực Hành": "green",
          "Kiểm Tra": "yellow"
        }[type] || "";
      }
    }
  };
  </script>
  
  <style scoped>
  .schedule-container {
    padding: 20px;
    text-align: center;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: center;
  }
  .blue {
    color: blue;
  }
  .green {
    color: green;
  }
  .yellow {
    color: orange;
  }
  button {
    margin-top: 5px;
    cursor: pointer;
  }
  </style>
  
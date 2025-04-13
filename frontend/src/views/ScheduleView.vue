<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-blue-800">Học Kỳ {{ currentSemester }} - Năm Học {{ currentYear }}</h1>
      
      <div class="flex items-center justify-between mt-4">
        <div class="flex space-x-2">
          <button @click="previousWeek" class="btn-primary">
            <i class="fas fa-chevron-left mr-1"></i> Tuần Trước
          </button>
          <h2 class="text-xl font-semibold">Tuần {{ currentWeek }} - Tháng {{ currentMonth }}/{{ currentYear }}</h2>
          <button @click="nextWeek" class="btn-primary">
            Tuần Sau <i class="fas fa-chevron-right ml-1"></i>
          </button>
        </div>
        
        <div class="flex space-x-4">
          <button @click="viewMode = 'week'" :class="{'btn-active': viewMode === 'week'}" class="btn-secondary">
            <i class="fas fa-calendar-week mr-1"></i> Tuần
          </button>
          <button @click="viewMode = 'month'" :class="{'btn-active': viewMode === 'month'}" class="btn-secondary">
            <i class="fas fa-calendar-alt mr-1"></i> Tháng
          </button>
          <button @click="viewMode = 'semester'" :class="{'btn-active': viewMode === 'semester'}" class="btn-secondary">
            <i class="fas fa-graduation-cap mr-1"></i> Học Kỳ
          </button>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
      <div class="grid grid-cols-6 bg-gray-100">
        <div class="p-4 border-r border-gray-200">
          <h3 class="font-semibold text-gray-600">Thời Gian</h3>
        </div>
        <template v-for="day in weekDays" :key="day.date">
          <div class="p-4 border-r border-gray-200">
            <h3 class="font-semibold text-gray-600">{{ day.name }}</h3>
            <p class="text-sm text-gray-500">{{ day.date }}</p>
          </div>
        </template>
      </div>

      <div class="divide-y divide-gray-200">
        <template v-for="timeSlot in timeSlots" :key="timeSlot.id">
          <div class="grid grid-cols-6">
            <div class="p-4 border-r border-gray-200">
              <p class="text-sm font-medium">{{ timeSlot.time }}</p>
              <p class="text-xs text-gray-500">Ca {{ timeSlot.period }}</p>
            </div>
            <template v-for="day in weekDays" :key="day.date">
              <div 
                class="p-4 border-r border-gray-200 min-h-[100px] relative group hover:bg-blue-50 cursor-pointer"
                @click="openScheduleForm(timeSlot, day)"
              >
                <template v-if="getSchedule(timeSlot, day)">
                  <div class="bg-blue-100 p-2 rounded">
                    <h4 class="font-medium text-blue-800">{{ getSchedule(timeSlot, day).subject }}</h4>
                    <p class="text-sm text-blue-600">Phòng: {{ getSchedule(timeSlot, day).room }}</p>
                    <p class="text-sm text-blue-600">GV: {{ getSchedule(timeSlot, day).teacher }}</p>
                  </div>
                </template>
                <div class="absolute top-2 right-2 hidden group-hover:block">
                  <button @click.stop="editSchedule(timeSlot, day)" class="text-blue-600 hover:text-blue-800 mr-2">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click.stop="deleteSchedule(timeSlot, day)" class="text-red-600 hover:text-red-800">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </template>
          </div>
        </template>
      </div>
    </div>

    <div class="mt-6">
      <div class="flex items-center space-x-4">
        <div class="flex items-center">
          <span class="w-4 h-4 bg-blue-500 rounded-full mr-2"></span>
          <span>Lý Thuyết</span>
        </div>
        <div class="flex items-center">
          <span class="w-4 h-4 bg-green-500 rounded-full mr-2"></span>
          <span>Thực Hành</span>
        </div>
        <div class="flex items-center">
          <span class="w-4 h-4 bg-orange-500 rounded-full mr-2"></span>
          <span>Kiểm Tra</span>
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="showScheduleForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">{{ formMode === 'add' ? 'Thêm Lịch Học' : 'Chỉnh Sửa Lịch Học' }}</h2>
        <form @submit.prevent="submitScheduleForm">
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">Môn Học</label>
            <input v-model="scheduleForm.subject" type="text" class="form-input w-full" required>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">Giảng Viên</label>
            <input v-model="scheduleForm.teacher" type="text" class="form-input w-full" required>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">Phòng Học</label>
            <input v-model="scheduleForm.room" type="text" class="form-input w-full" required>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">Loại</label>
            <select v-model="scheduleForm.type" class="form-select w-full" required>
              <option value="theory">Lý Thuyết</option>
              <option value="practice">Thực Hành</option>
              <option value="exam">Kiểm Tra</option>
            </select>
          </div>
          <div class="flex justify-end space-x-2">
            <button type="button" @click="closeScheduleForm" class="btn-secondary">Hủy</button>
            <button type="submit" class="btn-primary">{{ formMode === 'add' ? 'Thêm' : 'Cập Nhật' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const currentSemester = ref(2)
const currentYear = ref('2023-2024')
const currentWeek = ref(1)
const currentMonth = ref(3)
const viewMode = ref('week')
const showScheduleForm = ref(false)
const formMode = ref('add')

const scheduleForm = ref({
  subject: '',
  teacher: '',
  room: '',
  type: 'theory'
})

const weekDays = ref([
  { name: 'Thứ 2', date: '18/03' },
  { name: 'Thứ 3', date: '19/03' },
  { name: 'Thứ 4', date: '20/03' },
  { name: 'Thứ 5', date: '21/03' },
  { name: 'Thứ 6', date: '22/03' }
])

const timeSlots = ref([
  { id: 1, time: '7:00 - 9:00', period: 1 },
  { id: 2, time: '9:15 - 11:15', period: 2 },
  { id: 3, time: '13:00 - 15:00', period: 3 },
  { id: 4, time: '15:15 - 17:15', period: 4 },
  { id: 5, time: '18:45 - 21:00', period: 5 }
])

const scheduleData = ref([])

const previousWeek = () => {
  currentWeek.value--
  // TODO: Update weekDays and scheduleData based on the new week
}

const nextWeek = () => {
  currentWeek.value++
  // TODO: Update weekDays and scheduleData based on the new week
}

const getSchedule = (timeSlot, day) => {
  return scheduleData.value.find(
    schedule => schedule.timeSlotId === timeSlot.id && schedule.date === day.date
  )
}

const openScheduleForm = (timeSlot, day) => {
  const existingSchedule = getSchedule(timeSlot, day)
  if (existingSchedule) {
    scheduleForm.value = { ...existingSchedule }
    formMode.value = 'edit'
  } else {
    scheduleForm.value = {
      subject: '',
      teacher: '',
      room: '',
      type: 'theory',
      timeSlotId: timeSlot.id,
      date: day.date
    }
    formMode.value = 'add'
  }
  showScheduleForm.value = true
}

const closeScheduleForm = () => {
  showScheduleForm.value = false
  scheduleForm.value = {
    subject: '',
    teacher: '',
    room: '',
    type: 'theory'
  }
}

const submitScheduleForm = () => {
  if (formMode.value === 'add') {
    scheduleData.value.push({ ...scheduleForm.value })
  } else {
    const index = scheduleData.value.findIndex(
      schedule => 
        schedule.timeSlotId === scheduleForm.value.timeSlotId && 
        schedule.date === scheduleForm.value.date
    )
    if (index !== -1) {
      scheduleData.value[index] = { ...scheduleForm.value }
    }
  }
  closeScheduleForm()
}

const editSchedule = (timeSlot, day) => {
  openScheduleForm(timeSlot, day)
}

const deleteSchedule = (timeSlot, day) => {
  const index = scheduleData.value.findIndex(
    schedule => schedule.timeSlotId === timeSlot.id && schedule.date === day.date
  )
  if (index !== -1) {
    scheduleData.value.splice(index, 1)
  }
}
</script>

<style scoped>
.btn-primary {
  @apply px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors;
}

.btn-secondary {
  @apply px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors;
}

.btn-active {
  @apply bg-blue-100 text-blue-700;
}

.form-input {
  @apply mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
}

.form-select {
  @apply mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
}
</style> 
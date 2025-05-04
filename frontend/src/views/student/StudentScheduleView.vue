<template>
  <div class="container-fluid calendar-view">
    <div class="card shadow mb-4">
      <div class="card-header py-3 d-flex justify-content-between align-items-center flex-wrap">
        <h5 class="m-0 font-weight-bold text-primary">
          <i class="bi bi-calendar-week me-2"></i>Lịch Học Sinh Viên
        </h5>
        <div class="d-flex align-items-center mt-2 mt-sm-0">
          <div class="btn-group viewToggle me-2">
            <button 
              type="button" 
              class="btn btn-sm" 
              :class="calendarView === 'timeGridWeek' ? 'btn-primary' : 'btn-outline-primary'"
              @click="calendarView = 'timeGridWeek'"
            >
              <i class="bi bi-calendar-week me-1"></i>Tuần
            </button>
            <button 
              type="button" 
              class="btn btn-sm" 
              :class="calendarView === 'dayGridMonth' ? 'btn-primary' : 'btn-outline-primary'"
              @click="calendarView = 'dayGridMonth'"
            >
              <i class="bi bi-calendar-month me-1"></i>Tháng
            </button>
            <button 
              type="button" 
              class="btn btn-sm" 
              :class="calendarView === 'listWeek' ? 'btn-primary' : 'btn-outline-primary'"
              @click="calendarView = 'listWeek'"
            >
              <i class="bi bi-list-ul me-1"></i>Danh sách
            </button>
          </div>
          
          <div class="btn-group">
            <button type="button" class="btn btn-sm btn-outline-secondary" @click="today">
              Hôm nay
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" @click="prev">
              <i class="bi bi-chevron-left"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" @click="next">
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
          
          <button type="button" class="btn btn-sm btn-outline-primary ms-2" @click="forceRefresh">
            <i class="bi bi-arrow-clockwise"></i>
          </button>
        </div>
      </div>
      
      <div class="card-body">
        <div class="row mb-4">
          <!-- Filter class -->
          <div class="col-md-6 mb-3 mb-md-0">
            <div class="form-group">
              <label><i class="bi bi-book me-1"></i>Lớp học</label>
              <select v-model="selectedClass" class="form-select" @change="applyFilters">
                <option value="">Tất cả lớp học</option>
                <option v-for="class_ in classes" :key="class_.id" :value="class_.id">
                  {{ class_.code }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="col-md-6 d-flex align-items-end justify-content-center">
            <h5 class="text-center mb-0 date-display">
              <span class="current-date-range">{{ currentDateRange }}</span>
            </h5>
          </div>
        </div>
        
        <!-- Loading indicator -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Đang tải...</span>
          </div>
          <p class="mt-2">Đang tải dữ liệu lịch học...</p>
        </div>
        
        <!-- Error message -->
        <div v-else-if="error" class="alert alert-danger" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          {{ error }}
        </div>
        
        <!-- Calendar -->
        <div v-else ref="calendarContainer" class="calendar-container">
          <FullCalendar 
            ref="fullCalendar"
            :options="calendarOptions" 
          />
        </div>
      </div>
    </div>
    
    <!-- Chi tiết sự kiện modal -->
    <div class="modal fade" id="eventModal" tabindex="-1" aria-labelledby="eventModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div 
            class="modal-header" 
            :class="'bg-primary text-white'"
          >
            <h5 class="modal-title" id="eventModalLabel">
              {{ selectedEvent?.title || 'Thông tin môn học' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="selectedEvent">
            <div class="mb-3">
              <p class="mb-1 fw-bold">Thời gian:</p>
              <p>{{ formatDate(selectedEvent.start) }} {{ formatTime(selectedEvent.start) }} - {{ formatTime(selectedEvent.end) }}</p>
            </div>
            <div class="mb-3">
              <p class="mb-1 fw-bold">Phòng học:</p>
              <p>{{ selectedEvent.extendedProps.classroom_number }}</p>
            </div>
            <div class="mb-3">
              <p class="mb-1 fw-bold">Tòa nhà:</p>
              <p>{{ selectedEvent.extendedProps.building_name }}</p>
            </div>
            <div class="mb-3">
              <p class="mb-1 fw-bold">Cơ sở:</p>
              <p>{{ selectedEvent.extendedProps.campus_name }}</p>
            </div>
            <div class="mb-3">
              <p class="mb-1 fw-bold">Mã môn:</p>
              <p>{{ selectedEvent.extendedProps.subject_code }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import axios from 'axios';
import { Modal } from 'bootstrap';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';
import viLocale from '@fullcalendar/core/locales/vi';

// State
const loading = ref(false);
const error = ref(null);
const calendarView = ref('timeGridWeek');
const currentDateRange = ref('');
const scheduleData = ref([]);
const calendarEvents = ref([]);
const classes = ref([]);
const selectedClass = ref('');
const selectedEvent = ref(null);
const fullCalendar = ref(null);
const calendarContainer = ref(null);
let eventModal = null;
let resizeTimeout = null;
let resizeObserver = null;
let prevWidth = 0;
let prevHeight = 0;
let sidebarObserver = null;
let bodyObserver = null;

// Convert schedule data to calendar events
const processScheduleData = (data) => {
  if (!data || !data.length) return [];
  
  return data.map(schedule => {
    // Sử dụng một màu duy nhất cho tất cả các sự kiện
    const backgroundColor = '#0d6efd'; // Primary color
    const borderColor = '#0a58ca';

    // Tạo event với ngày cụ thể thay vì lặp theo ngày trong tuần
    return {
      id: schedule.id.toString(),
      title: schedule.subject_name,
      start: `${schedule.specific_date}T${schedule.start_time}`,
      end: `${schedule.specific_date}T${schedule.end_time}`,
      backgroundColor,
      borderColor,
      textColor: '#fff',
      extendedProps: {
        subject_code: schedule.subject_code,
        classroom_number: schedule.classroom_number,
        building_name: schedule.building_name,
        campus_name: schedule.campus_name
      }
    };
  });
};

// Calendar options
const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin],
  headerToolbar: false, // We're using custom buttons
  initialView: calendarView.value,
  locale: viLocale,
  events: calendarEvents.value,
  firstDay: 1, // Monday as first day
  slotMinTime: '07:00:00',
  slotMaxTime: '21:30:00',
  allDaySlot: false,
  height: 'auto',
  contentHeight: 'auto',
  aspectRatio: 1.8, // This helps control the width/height ratio
  eventClick: handleEventClick,
  eventTimeFormat: {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  },
  datesSet: (info) => {
    // Chỉ cập nhật hiển thị ngày, không gọi API
    const start = info.start;
    const end = info.end;
    
    // Format the date range for display
    const startMonth = start.getMonth() + 1;
    const endMonth = end.getMonth() + 1;
    const startDate = start.getDate();
    const endDate = end.getDate() - 1; // End date is exclusive
    
    if (calendarView.value === 'dayGridMonth') {
      // For month view
      currentDateRange.value = `Tháng ${startMonth}/${start.getFullYear()}`;
    } else {
      // For week or list view
      currentDateRange.value = `${startDate}/${startMonth} - ${endDate}/${endMonth}/${end.getFullYear()}`;
    }
  },
  dayHeaderFormat: { weekday: 'long', day: 'numeric', month: 'numeric' },
  slotLabelFormat: {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  },
  views: {
    timeGridWeek: {
      titleFormat: { year: 'numeric', month: 'long', day: 'numeric' }
    },
    dayGridMonth: {
      titleFormat: { year: 'numeric', month: 'long' }
    },
    listWeek: {
      titleFormat: { year: 'numeric', month: 'long' }
    }
  }
}));

// Force refresh calendar
const forceRefresh = () => {
  if (fullCalendar.value) {
    // Hiển thị loading
    loading.value = true;
    
    // Gọi lại API để lấy dữ liệu mới
    fetchSchedules();
    
    // Cập nhật kích thước calendar
    const calendarApi = fullCalendar.value.getApi();
    calendarApi.updateSize();
    
    // Hiện sự kiện đang được chọn trước đó
    if (calendarView.value === 'dayGridMonth') {
      calendarApi.changeView('dayGridMonth');
    } else if (calendarView.value === 'timeGridWeek') {
      calendarApi.changeView('timeGridWeek');
    } else if (calendarView.value === 'listWeek') {
      calendarApi.changeView('listWeek');
    }
  }
};

// Handle resize observer
const setupResizeObserver = () => {
  if (!calendarContainer.value) return;
  
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
  
  // Create new ResizeObserver
  resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      const { width, height } = entry.contentRect;
      
      // Check if size actually changed significantly (more than 5px)
      if (Math.abs(width - prevWidth) > 3 || Math.abs(height - prevHeight) > 3) {
        prevWidth = width;
        prevHeight = height;
        
        if (fullCalendar.value) {
          const calendarApi = fullCalendar.value.getApi();
          calendarApi.updateSize();
          // console.log('Calendar size updated due to container resize:', width, height);
        }
      }
    }
  });
  
  // Start observing
  resizeObserver.observe(calendarContainer.value);
};

// Watch for DOM changes that affect layout
const setupDOMObservers = () => {
  // Watch for changes in the sidebar width
  const sidebar = document.querySelector('.sidebar, #sidebar, .side-nav, #sidebarMenu');
  
  if (sidebar && !sidebarObserver) {
    sidebarObserver = new MutationObserver(() => {
      // When sidebar changes, immediately update and set multiple delayed updates
      updateCalendarSize();
      
      // Additional updates with delays to catch transitions
      for (let i = 1; i <= 10; i++) {
        setTimeout(updateCalendarSize, i * 100);
      }
    });
    
    sidebarObserver.observe(sidebar, {
      attributes: true,
      attributeFilter: ['class', 'style'],
      childList: false,
      subtree: false
    });
  }
  
  // Watch for changes to the body class
  const body = document.body;
  
  if (!bodyObserver) {
    bodyObserver = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
          // Sidebar might have been toggled via body class
          updateCalendarSize();
          
          // Multiple delayed updates to catch transitions
          for (let i = 1; i <= 10; i++) {
            setTimeout(updateCalendarSize, i * 100);
          }
        }
      }
    });
    
    bodyObserver.observe(body, {
      attributes: true,
      attributeFilter: ['class'],
      childList: false,
      subtree: false
    });
  }
  
  // Find sidebar toggle buttons and attach direct event listeners
  document.querySelectorAll('[data-toggle="sidebar"], .sidebar-toggle, .navbar-toggler, #sidebarToggle, .nav-link').forEach(button => {
    button.addEventListener('click', () => {
      // Update immediately and multiple times during the transition
      updateCalendarSize();
      for (let i = 1; i <= 15; i++) {
        setTimeout(updateCalendarSize, i * 100);
      }
    });
  });
};

// Handle window resize to update calendar size
const handleResize = () => {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  
  resizeTimeout = setTimeout(() => {
    if (fullCalendar.value) {
      const calendarApi = fullCalendar.value.getApi();
      calendarApi.updateSize();
      
      // Try again after a short delay
      setTimeout(() => {
        calendarApi.updateSize();
      }, 200);
    }
  }, 100);
};

// Handle calendar event click
const handleEventClick = (info) => {
  selectedEvent.value = info.event;
  if (!eventModal) {
    eventModal = new Modal(document.getElementById('eventModal'));
  }
  eventModal.show();
};

// Format date for display in modal
const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  const dayNames = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
  const dayName = dayNames[d.getDay()];
  
  // Format: Thứ 2, 20/05/2023
  return `${dayName}, ${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getFullYear()}`;
};

// Format time for display in modal
const formatTime = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false });
};

// Force update calendar size
const updateCalendarSize = () => {
  nextTick(() => {
    if (fullCalendar.value) {
      const calendarApi = fullCalendar.value.getApi();
      calendarApi.updateSize();
    }
  });
};

// Calendar navigation methods - không gọi API khi chuyển đổi view
const prev = () => {
  if (fullCalendar.value) {
    const calendarApi = fullCalendar.value.getApi();
    calendarApi.prev();
  }
};

const next = () => {
  if (fullCalendar.value) {
    const calendarApi = fullCalendar.value.getApi();
    calendarApi.next();
  }
};

const today = () => {
  if (fullCalendar.value) {
    const calendarApi = fullCalendar.value.getApi();
    calendarApi.today();
  }
};

// API Calls - chỉ gọi 1 lần khi khởi tạo
const fetchSchedules = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // Get auth token
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
      error.value = 'Bạn cần đăng nhập lại để xem lịch học.';
      loading.value = false;
      return;
    }
    
    // Fetch tất cả lịch học không giới hạn thời gian
    const response = await axios.get('http://localhost:5000/api/schedules', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.data && response.data.items) {
      scheduleData.value = response.data.items;
      calendarEvents.value = processScheduleData(scheduleData.value);
    } else {
      scheduleData.value = [];
      calendarEvents.value = [];
    }
  } catch (err) {
    console.error('Error fetching schedules:', err);
    error.value = 'Không thể tải lịch học. Vui lòng thử lại sau.';
    scheduleData.value = [];
    calendarEvents.value = [];
  } finally {
    loading.value = false;
    // Update calendar size after data loads
    updateCalendarSize();
  }
};

const fetchClasses = async () => {
  try {
    // Get auth token
    const token = localStorage.getItem('auth_token');
    const studentId = localStorage.getItem('student_id');
    
    if (!token || !studentId) {
      console.error('Missing auth token or student ID');
      return;
    }
    
    // Use the actual API endpoint shown in the logs with auth token
    const response = await axios.get(`http://localhost:5000/api/class_students/student/${studentId}/classes`, {
      headers: {
        'Authorization': token
      }
    });
    
    if (response.data && response.data.items) {
      classes.value = response.data.items;
    }
  } catch (err) {
    console.error('Error fetching classes:', err);
  }
};

// Apply filters
const applyFilters = () => {
  fetchSchedules();
};

// Watch for view mode changes
watch(calendarView, () => {
  if (fullCalendar.value) {
    const calendarApi = fullCalendar.value.getApi();
    calendarApi.changeView(calendarView.value);
    // Update size after view change
    nextTick(() => {
      calendarApi.updateSize();
    });
  }
});

// Setup event listeners
onMounted(() => {
  fetchClasses();
  // Chỉ gọi fetchSchedules một lần duy nhất lúc khởi tạo
  fetchSchedules();
  
  // Add resize listener
  window.addEventListener('resize', handleResize);
  
  // Initialize resize observer for calendar container
  nextTick(() => {
    if (calendarContainer.value) {
      prevWidth = calendarContainer.value.offsetWidth;
      prevHeight = calendarContainer.value.offsetHeight;
      setupResizeObserver();
    }
    
    // Setup DOM observers
    setupDOMObservers();
    
    // Force update calendar size
    setTimeout(updateCalendarSize, 500);
    
    // Additional delayed updates
    setTimeout(updateCalendarSize, 1000);
    setTimeout(updateCalendarSize, 2000);
  });
});

// Clean up event listeners
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  if (sidebarObserver) {
    sidebarObserver.disconnect();
    sidebarObserver = null;
  }
  if (bodyObserver) {
    bodyObserver.disconnect();
    bodyObserver = null;
  }
});
</script>

<style scoped>
.calendar-view {
  width: 100%;
  transition: all 0.3s ease;
  overflow-x: hidden; /* Prevent horizontal overflow */
}

.calendar-container {
  height: 650px;
  width: 100%;
  position: relative;
  max-width: 100%;
  overflow-x: hidden; /* Ensure no horizontal overflow */
}

.color-box {
  display: inline-block;
  width: 14px;
  height: 14px;
  margin-right: 5px;
  border-radius: 2px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-right: 1rem;
}

.current-date-range {
  font-size: 1.1rem;
  font-weight: 500;
}

.viewToggle .btn:focus {
  box-shadow: none;
}

.date-display {
  width: 100%;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .calendar-container {
    height: 550px;
  }
  
  .current-date-range {
    font-size: 0.9rem;
  }
}

@media (max-width: 576px) {
  .calendar-container {
    height: 450px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start !important;
  }
  
  .card-header h5 {
    margin-bottom: 0.5rem;
  }
}

/* Custom calendar styles */
:deep(.fc-timegrid-slot-minor) {
  border-top-style: dashed;
}

:deep(.fc-timegrid-now-indicator-line) {
  border-color: #dc3545;
  border-width: 2px;
}

:deep(.fc-event) {
  border-radius: 3px;
  cursor: pointer;
}

:deep(.fc-event:hover) {
  transform: scale(1.005);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
}

:deep(.fc-header-toolbar) {
  margin-bottom: 0.5rem !important;
}

:deep(.fc-view-harness) {
  background-color: #fff;
  border-radius: 5px;
}

:deep(.fc-list-event-title) {
  font-weight: 500;
}

:deep(.fc-day-today) {
  background-color: rgba(13, 110, 253, 0.05) !important;
}

/* Ensure calendar resizes properly */
:deep(.fc) {
  width: 100% !important; 
  max-width: 100% !important;
  overflow-x: hidden !important;
}

:deep(.fc-scrollgrid) {
  max-width: 100%;
  overflow-x: hidden !important;
}

:deep(.fc-scrollgrid-sync-table) {
  width: 100% !important;
  max-width: 100% !important;
}

:deep(.fc-view-harness) {
  width: 100% !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
}

/* Ensure all days fit */
:deep(.fc-col-header-cell) {
  min-width: auto !important;
  width: auto !important;
}

:deep(.fc-timegrid-body) {
  overflow-x: hidden !important;
}

:deep(.fc-timegrid-body-container) {
  overflow-x: hidden !important;
}

/* Adjust header styles for small screens */
@media (max-width: 768px) {
  :deep(.fc-col-header-cell-cushion) {
    font-size: 0.9rem;
  }
  
  :deep(.fc-timegrid-slot-label) {
    font-size: 0.8rem;
  }
  
  :deep(.fc-event-title) {
    font-size: 0.85rem;
  }
}
</style> 
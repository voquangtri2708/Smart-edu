<template>
  <div class="pagination-component">
    <!-- Page size selector -->
    <div class="d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center">
        <label class="me-2">Hiển thị:</label>
        <select class="form-select form-select-sm" v-model.number="localPageSize" @change="onPageSizeChange" style="width: auto;">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
        </select>
        <span class="ms-2">/ trang</span>
        <span class="ms-3">Tổng số: {{ totalItems }} {{ itemLabel }}</span>
      </div>
      
      <nav aria-label="Page navigation">
        <ul class="pagination">
          <!-- First page button -->
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="onPageChange(1)" aria-label="First">
              <span aria-hidden="true">&laquo;&laquo;</span>
            </a>
          </li>
          
          <!-- Previous page button -->
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="onPageChange(currentPage - 1)" aria-label="Previous">
              <span aria-hidden="true">&laquo;</span>
            </a>
          </li>
          
          <!-- Page numbers -->
          <li v-for="page in getPaginationRange()" :key="page" class="page-item" 
              :class="{ active: page === currentPage, disabled: page === '...' }">
            <a v-if="page !== '...'" class="page-link" href="#" @click.prevent="onPageChange(page)">{{ page }}</a>
            <span v-else class="page-link">{{ page }}</span>
          </li>
          
          <!-- Next page button -->
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="onPageChange(currentPage + 1)" aria-label="Next">
              <span aria-hidden="true">&raquo;</span>
            </a>
          </li>
          
          <!-- Last page button -->
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="onPageChange(totalPages)" aria-label="Last">
              <span aria-hidden="true">&raquo;&raquo;</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  pageSizeOptions: {
    type: Array,
    default: () => [5, 10, 20, 50, 100]
  },
  itemLabel: {
    type: String,
    default: 'mục'
  }
});

const emit = defineEmits(['page-change', 'page-size-change']);

// Local state to avoid direct prop mutation
const localPageSize = ref(Number(props.pageSize));

// Watch pageSize prop changes
watch(() => props.pageSize, (newVal) => {
  localPageSize.value = Number(newVal);
});

// Methods
const getPaginationRange = () => {
  // Only show a limited window of page numbers
  const delta = 2; // Number of pages to show on each side of current page
  let range = [];
  
  // Always show first page
  range.push(1);
  
  // Calculate the start and end of the pagination window
  const rangeStart = Math.max(2, props.currentPage - delta);
  const rangeEnd = Math.min(props.totalPages - 1, props.currentPage + delta);
  
  // Add ellipsis after first page if needed
  if (rangeStart > 2) {
    range.push('...');
  }
  
  // Add pages in the middle window
  for (let i = rangeStart; i <= rangeEnd; i++) {
    range.push(i);
  }
  
  // Add ellipsis before last page if needed
  if (rangeEnd < props.totalPages - 1) {
    range.push('...');
  }
  
  // Always show last page if it exists
  if (props.totalPages > 1) {
    range.push(props.totalPages);
  }
  
  return range;
};

const onPageChange = (page) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('page-change', page);
  }
};

const onPageSizeChange = () => {
  emit('page-size-change', Number(localPageSize.value));
};
</script>

<style scoped>
.pagination-component {
  margin-top: 1rem;
}

.pagination {
  margin-bottom: 0;
}
</style> 
        <!-- Student Menu Items -->
        <template v-if="role === 'student'">
          <li class="nav-item">
            <router-link class="nav-link" :to="{ name: 'student-schedule'}" :class="{ active: isActiveRoute('student-schedule') }">
              <i class="bi bi-calendar-week"></i>
              <span>Lịch học</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" :to="{ name: 'student-exam-schedule'}" :class="{ active: isActiveRoute('student-exam-schedule') }">
              <i class="bi bi-journal-check"></i>
              <span>Lịch kiểm tra</span>
            </router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link cursor-pointer" :class="{ active: isActiveRoute('student-feedbacks') }" @click="goToFeedbacks">
              <i class="bi bi-chat-square-text"></i>
              <span>Đánh giá</span>
            </a>
          </li>
        </template> 
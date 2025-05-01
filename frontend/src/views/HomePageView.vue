<template>
  <div class="container py-4">
    <div class="card shadow-sm mb-4">
      <div class="card-header bg-primary text-white">
        <h3 class="mb-0"><i class="bi bi-book me-2"></i>Nội quy sử dụng hệ thống SMART-EDU</h3>
      </div>
      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-12">
            <div class="alert alert-info">
              <i class="bi bi-info-circle-fill me-2"></i>
              <strong>Chào mừng bạn đến với hệ thống quản lý giáo dục SMART-EDU!</strong> 
              Vui lòng đọc kỹ nội quy sử dụng hệ thống để đảm bảo môi trường học tập hiệu quả và an toàn.
            </div>
          </div>
        </div>

        <!-- Quy tắc chung -->
        <div class="card mb-4 border-0 shadow-sm">
          <div class="card-header bg-light d-flex align-items-center">
            <i class="bi bi-shield-check me-2 text-primary fs-4"></i>
            <h5 class="mb-0">Quy tắc chung</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover">
                <tbody>
                  <tr>
                    <td class="text-center" style="width: 50px"><i class="bi bi-check-circle text-success"></i></td>
                    <td>Mỗi người dùng chỉ được sử dụng một tài khoản duy nhất do nhà trường cấp.</td>
                  </tr>
                  <tr>
                    <td class="text-center"><i class="bi bi-check-circle text-success"></i></td>
                    <td>Bảo mật thông tin tài khoản, không chia sẻ mật khẩu với người khác.</td>
                  </tr>
                  <tr>
                    <td class="text-center"><i class="bi bi-check-circle text-success"></i></td>
                    <td>Tuân thủ các quy định về đạo đức học tập và giao tiếp trên môi trường số.</td>
                  </tr>
                  <tr>
                    <td class="text-center"><i class="bi bi-check-circle text-success"></i></td>
                    <td>Không sử dụng hệ thống vào mục đích phi giáo dục hoặc các hoạt động phi pháp.</td>
                  </tr>
                  <tr>
                    <td class="text-center"><i class="bi bi-check-circle text-success"></i></td>
                    <td>Thông báo ngay cho quản trị viên khi phát hiện lỗi bảo mật hoặc vấn đề kỹ thuật.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="row">
          <!-- Quy định đối với sinh viên -->
          <div class="col-lg-6">
            <div class="card mb-4 border-0 shadow-sm h-100">
              <div class="card-header bg-light d-flex align-items-center">
                <i class="bi bi-mortarboard me-2 text-primary fs-4"></i>
                <h5 class="mb-0">Đối với sinh viên</h5>
              </div>
              <div class="card-body">
                <ul class="list-group list-group-flush">
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Kiểm tra lịch học và thông báo thường xuyên trên hệ thống.</span>
                  </li>
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Tham gia đánh giá giảng viên và phòng học theo quy định của nhà trường.</span>
                  </li>
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Cập nhật thông tin cá nhân kịp thời khi có thay đổi.</span>
                  </li>
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Nộp bài tập đúng thời hạn và tuân thủ quy định về bản quyền.</span>
                  </li>
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Tham gia khảo sát và góp ý để cải thiện chất lượng đào tạo.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
          
          <!-- Quy định đối với giảng viên -->
          <div class="col-lg-6">
            <div class="card mb-4 border-0 shadow-sm h-100">
              <div class="card-header bg-light d-flex align-items-center">
                <i class="bi bi-person-video3 me-2 text-primary fs-4"></i>
                <h5 class="mb-0">Đối với giảng viên</h5>
              </div>
              <div class="card-body">
                <ul class="list-group list-group-flush">
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Cập nhật tài liệu giảng dạy và thông báo lớp học đúng hạn.</span>
                  </li>
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Đánh giá và chấm điểm sinh viên công bằng và minh bạch.</span>
                  </li>
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Phản hồi thắc mắc của sinh viên trong thời gian quy định.</span>
                  </li>
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Tuân thủ lịch giảng dạy và thông báo trước khi có thay đổi.</span>
                  </li>
                  <li class="list-group-item d-flex align-items-start">
                    <i class="bi bi-arrow-right-circle text-primary me-2 mt-1"></i>
                    <span>Tham gia đánh giá và cải tiến chương trình đào tạo.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <div class="row">
          <!-- Quy định về sử dụng hệ thống -->
          <div class="col-lg-6">
            <div class="card mb-4 border-0 shadow-sm h-100">
              <div class="card-header bg-light d-flex align-items-center">
                <i class="bi bi-laptop me-2 text-primary fs-4"></i>
                <h5 class="mb-0">Sử dụng hệ thống</h5>
              </div>
              <div class="card-body">
                <div class="d-flex align-items-start mb-3">
                  <div class="bg-light rounded-circle p-2 me-3">
                    <i class="bi bi-clock text-primary"></i>
                  </div>
                  <div>
                    <h6 class="fw-bold">Thời gian truy cập</h6>
                    <p class="mb-0">Hệ thống hoạt động 24/7, nhưng có thể bảo trì định kỳ vào ngày Chủ nhật (22:00-24:00).</p>
                  </div>
                </div>
                
                <div class="d-flex align-items-start mb-3">
                  <div class="bg-light rounded-circle p-2 me-3">
                    <i class="bi bi-exclamation-triangle text-warning"></i>
                  </div>
                  <div>
                    <h6 class="fw-bold">Hành vi cấm</h6>
                    <p class="mb-0">Nghiêm cấm tấn công, phá hoại hệ thống hoặc cố tình gây quá tải.</p>
                  </div>
                </div>
                
                <div class="d-flex align-items-start">
                  <div class="bg-light rounded-circle p-2 me-3">
                    <i class="bi bi-shield-lock text-primary"></i>
                  </div>
                  <div>
                    <h6 class="fw-bold">Bảo mật</h6>
                    <p class="mb-0">Đăng xuất khi không sử dụng và thay đổi mật khẩu định kỳ 3 tháng/lần.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Xử lý vi phạm -->
          <div class="col-lg-6">
            <div class="card mb-4 border-0 shadow-sm h-100">
              <div class="card-header bg-light d-flex align-items-center">
                <i class="bi bi-exclamation-diamond me-2 text-primary fs-4"></i>
                <h5 class="mb-0">Xử lý vi phạm</h5>
              </div>
              <div class="card-body">
                <div class="alert alert-warning">
                  <p class="fw-bold mb-2">Các hình thức xử lý vi phạm:</p>
                  <ol class="mb-0">
                    <li>Nhắc nhở, cảnh báo qua email</li>
                    <li>Khóa tài khoản tạm thời (1-7 ngày)</li>
                    <li>Khóa tài khoản vĩnh viễn</li>
                    <li>Xử lý theo quy chế của nhà trường</li>
                  </ol>
                </div>
                
                <p class="text-muted fst-italic">
                  <i class="bi bi-info-circle me-1"></i>
                  Mức độ xử lý sẽ tùy thuộc vào tính chất và mức độ nghiêm trọng của vi phạm.
                </p>

                <div class="d-flex align-items-center mt-3">
                  <i class="bi bi-telephone-fill text-success me-2"></i>
                  <span>Hỗ trợ kỹ thuật: <strong>support@smart-edu.vn</strong></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Cam kết tuân thủ -->
        <div class="card border-0 bg-light mt-2">
          <div class="card-body">
            <p class="mb-0 text-center">
              <i class="bi bi-check2-circle text-success me-2"></i>
              <em>Việc sử dụng hệ thống SMART-EDU đồng nghĩa với việc bạn đã đọc, hiểu và đồng ý tuân thủ các quy định trên.</em>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Không cần logic đặc biệt cho trang này
</script>

<style scoped>
.card-header {
  border-bottom: none;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.bg-light {
  background-color: #f8f9fa !important;
}

.list-group-item {
  border-left: none;
  border-right: none;
  padding-left: 0;
  padding-right: 0;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}

.rounded-circle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
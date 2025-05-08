<!-- FaceRecognition.vue -->
<template>
  <div class="face-recognition-container">
    <div class="card">
      <div class="card-header">
        <h4>Xác thực khuôn mặt</h4>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center my-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Đang xử lý...</span>
          </div>
          <p class="mt-2">Đang xử lý...</p>
        </div>
        
        <div v-else-if="verificationStatus === 'not_started'" class="text-center">
          <div class="mb-4">
            <i class="bi bi-camera-video fs-1 text-primary"></i>
            <p class="mt-2">Vui lòng xác thực khuôn mặt để tiếp tục</p>
          </div>
          
          <div class="webcam-container mb-3 position-relative">
            <video ref="webcamVideo" class="border rounded w-100" :class="{'d-none': !cameraActive}" height="350" autoplay></video>
            <canvas ref="webcamCanvas" class="d-none"></canvas>
            <div v-if="!cameraActive" class="webcam-placeholder border rounded d-flex flex-column align-items-center justify-content-center" style="height: 350px;">
              <i class="bi bi-camera-video-off fs-1 text-secondary"></i>
              <p class="text-muted mt-2">Camera chưa được kích hoạt</p>
            </div>
            
            <div v-if="isTakingPhoto" class="webcam-overlay">
              <div class="spinner-border text-light" role="status">
                <span class="visually-hidden">Đang chụp ảnh...</span>
              </div>
            </div>
          </div>
          
          <div class="mb-3">
            <button v-if="!cameraActive" class="btn btn-primary" @click="startCamera">
              <i class="bi bi-camera-video me-1"></i>Bật camera
            </button>
            <button v-else class="btn btn-success" @click="captureAndVerify" :disabled="isTakingPhoto">
              <i class="bi bi-camera me-1"></i>Chụp và xác thực
            </button>
          </div>
          
          <p class="text-muted small">
            <i class="bi bi-info-circle me-1"></i>
            Đảm bảo bạn đang ở trong một khu vực có ánh sáng tốt và nhìn thẳng vào camera
          </p>
        </div>
        
        <div v-else-if="verificationStatus === 'success'" class="text-center">
          <div class="mb-4">
            <i class="bi bi-check-circle fs-1 text-success"></i>
            <h5 class="mt-2">Xác thực thành công!</h5>
            <p>Xin chào, {{ userInfo.last_name }} {{ userInfo.first_name }}</p>
          </div>
          
          <div class="mb-3">
            <button class="btn btn-primary" @click="continueToExam">
              <i class="bi bi-arrow-right me-1"></i>Tiếp tục làm bài
            </button>
          </div>
        </div>
        
        <div v-else-if="verificationStatus === 'error'" class="text-center">
          <div class="mb-4">
            <i class="bi bi-x-circle fs-1 text-danger"></i>
            <h5 class="mt-2">Xác thực thất bại</h5>
            <p>{{ errorMessage }}</p>
          </div>
          
          <div class="mb-3">
            <button class="btn btn-secondary me-2" @click="resetVerification">
              <i class="bi bi-arrow-counterclockwise me-1"></i>Thử lại
            </button>
            <button class="btn btn-outline-danger" @click="cancel">
              <i class="bi bi-x me-1"></i>Hủy
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import api from '@/utils/api';

export default {
  name: 'FaceRecognition',
  
  props: {
    examId: {
      type: [String, Number],
      required: true
    }
  },
  
  emits: ['verification-success', 'verification-cancel'],
  
  setup(props, { emit }) {
    const webcamVideo = ref(null);
    const webcamCanvas = ref(null);
    const cameraActive = ref(false);
    const isTakingPhoto = ref(false);
    const loading = ref(false);
    const verificationStatus = ref('not_started'); // not_started, success, error
    const errorMessage = ref('');
    const userInfo = ref({});
    
    let videoStream = null;
    
    onMounted(() => {
      // No automatic camera start
    });
    
    onBeforeUnmount(() => {
      stopCamera();
    });
    
    const startCamera = async () => {
      try {
        // Request access to webcam
        videoStream = await navigator.mediaDevices.getUserMedia({ 
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
          } 
        });
        
        // Set video source to webcam stream
        webcamVideo.value.srcObject = videoStream;
        cameraActive.value = true;
      } catch (error) {
        console.error('Error accessing webcam:', error);
        errorMessage.value = 'Không thể truy cập webcam. Vui lòng kiểm tra lại quyền truy cập.';
        verificationStatus.value = 'error';
      }
    };
    
    const stopCamera = () => {
      if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
      }
      
      if (webcamVideo.value && webcamVideo.value.srcObject) {
        webcamVideo.value.srcObject = null;
      }
      
      cameraActive.value = false;
    };
    
    const captureAndVerify = async () => {
      if (!cameraActive.value) return;
      
      isTakingPhoto.value = true;
      
      try {
        // Draw current video frame to canvas
        const canvas = webcamCanvas.value;
        const video = webcamVideo.value;
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to base64 image
        const imageData = canvas.toDataURL('image/jpeg');
        const base64Image = imageData.split(',')[1];
        
        // Verify face
        await verifyFace(base64Image);
      } catch (error) {
        console.error('Error during face verification:', error);
        errorMessage.value = 'Có lỗi xảy ra trong quá trình xác thực. Vui lòng thử lại.';
        verificationStatus.value = 'error';
      } finally {
        isTakingPhoto.value = false;
      }
    };
    
    const verifyFace = async (base64Image) => {
      loading.value = true;
      
      try {
        // Thử lấy ID từ nhiều nguồn khác nhau
        const studentId = localStorage.getItem('student_id');
        
        console.log("Các ID có sẵn:", {
          student_id: localStorage.getItem('student_id'),
          user_id: localStorage.getItem('user_id'),
          teacher_id: localStorage.getItem('teacher_id')
        });
        
        if (!studentId) {
          console.error("Không tìm thấy student_id trong localStorage");
          errorMessage.value = 'Không tìm thấy ID học sinh. Vui lòng đăng nhập lại.';
          verificationStatus.value = 'error';
          return;
        }
        
        console.log("Đang gửi student_id để xác thực:", studentId);
        
        const response = await api.post('/recognize-face', {
          image: base64Image,
          role: 'student',
          expected_id: studentId.trim() // Đảm bảo không có khoảng trắng
        });
        
        console.log("Kết quả xác thực:", response.data);
        
        if (response.data.recognized) {
          // Xem ID có khớp nhau không (So sánh chuỗi)
          const expectedId = String(studentId).trim();
          const recognizedId = String(response.data.user.id).trim();
          
          console.log("So sánh ID:", {
            expected: expectedId,
            recognized: recognizedId,
            isEqual: expectedId === recognizedId,
            expectedLength: expectedId.length,
            recognizedLength: recognizedId.length
          });
          
          // Kiểm tra xem người được nhận diện có phải là người đang đăng nhập không
          if (response.data.matched_expected || expectedId === recognizedId) {
            // Xác thực thành công và đúng người
            userInfo.value = response.data.user;
            verificationStatus.value = 'success';
            stopCamera(); // Stop camera after successful verification
          } else {
            // Nhận diện thành công nhưng không phải người đang đăng nhập
            console.error("ID không khớp:", {
              recognized_id: recognizedId,
              expected_id: expectedId
            });
            errorMessage.value = 'Khuôn mặt được nhận diện không khớp với tài khoản đang đăng nhập.';
            verificationStatus.value = 'error';
          }
        } else {
          // Verification failed
          errorMessage.value = response.data.message || 'Không nhận diện được khuôn mặt. Vui lòng thử lại.';
          verificationStatus.value = 'error';
        }
      } catch (error) {
        console.error('API error during face verification:', error);
        errorMessage.value = error.response?.data?.message || 'Lỗi kết nối với máy chủ. Vui lòng thử lại sau.';
        verificationStatus.value = 'error';
      } finally {
        loading.value = false;
      }
    };
    
    const resetVerification = () => {
      verificationStatus.value = 'not_started';
      errorMessage.value = '';
      
      // Dừng camera hiện tại trước
      stopCamera();
      
      // Đặt timeout để đảm bảo camera đã dừng hoàn toàn trước khi khởi động lại
      setTimeout(() => {
        startCamera();
      }, 500);
    };
    
    const continueToExam = () => {
      emit('verification-success', userInfo.value);
    };
    
    const cancel = () => {
      stopCamera();
      emit('verification-cancel');
    };
    
    return {
      webcamVideo,
      webcamCanvas,
      cameraActive,
      isTakingPhoto,
      loading,
      verificationStatus,
      errorMessage,
      userInfo,
      startCamera,
      captureAndVerify,
      resetVerification,
      continueToExam,
      cancel
    };
  }
};
</script>

<style scoped>
.face-recognition-container {
  max-width: 600px;
  margin: 0 auto;
}

.webcam-placeholder,
.webcam-container {
  background-color: #f8f9fa;
  border-radius: 4px;
}

.webcam-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}
</style> 
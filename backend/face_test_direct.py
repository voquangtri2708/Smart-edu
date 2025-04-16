import cv2
import numpy as np
import torch
from PIL import Image
import time
import sys
import os
import mysql.connector
import json

def encode_face_from_frame(frame):
    """Trích xuất face embedding từ frame"""
    # Import các module cần thiết
    from facenet_pytorch import MTCNN, InceptionResnetV1
    
    # Khởi tạo mô hình
    mtcnn = MTCNN(image_size=160, margin=20)
    resnet = InceptionResnetV1(pretrained='vggface2').eval()
    
    # Chuyển từ BGR (OpenCV) sang RGB (PIL)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)
    
    # Nhận diện và trích xuất khuôn mặt
    face = mtcnn(pil_img)
    
    if face is not None:
        face = face.unsqueeze(0)  # [1, 3, 160, 160]
        with torch.no_grad():
            embedding = resnet(face).squeeze().tolist()
        return embedding
    else:
        return None

def check_face(face_embedding, db_embedding, threshold=0.8):
    """Kiểm tra xem hai khuôn mặt có khớp không"""
    dist = np.linalg.norm(np.array(face_embedding) - np.array(db_embedding))
    print(f"Face distance: {dist}, threshold: {threshold}")
    return dist < threshold

def connect_to_db():
    """Kết nối trực tiếp đến database"""
    # Điều chỉnh thông tin kết nối database nếu cần
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="181003",
        database="smartedu1"
    )
    return db

def get_face_data():
    """Lấy dữ liệu face_encoding từ database"""
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)
    
    # Lấy dữ liệu từ bảng student
    cursor.execute("SELECT id, first_name, last_name, face_encoding FROM student WHERE face_encoding IS NOT NULL")
    students = cursor.fetchall()
    
    # Lấy dữ liệu từ bảng teacher
    cursor.execute("SELECT id, first_name, last_name, face_encoding FROM teacher WHERE face_encoding IS NOT NULL")
    teachers = cursor.fetchall()
    
    # Chuyển đổi JSON string thành Python object
    for student in students:
        if student['face_encoding']:
            student['face_encoding'] = json.loads(student['face_encoding'])
    
    for teacher in teachers:
        if teacher['face_encoding']:
            teacher['face_encoding'] = json.loads(teacher['face_encoding'])
    
    cursor.close()
    db.close()
    
    return students, teachers

def main():
    # Lấy dữ liệu khuôn mặt từ database
    students, teachers = get_face_data()
    print(f"Đã tải {len(students)} sinh viên và {len(teachers)} giảng viên có dữ liệu khuôn mặt")
    
    # Khởi tạo camera
    cap = cv2.VideoCapture(0)
    
    last_process_time = 0
    process_interval = 0.5  # Giây giữa mỗi lần xử lý
    
    while True:
        # Đọc frame từ camera
        ret, frame = cap.read()
        if not ret:
            break
            
        # Hiển thị frame
        display_frame = frame.copy()
        
        current_time = time.time()
        # Xử lý mỗi process_interval giây một lần
        if current_time - last_process_time > process_interval:
            last_process_time = current_time
            
            # Trích xuất embedding từ frame
            face_embedding = encode_face_from_frame(frame)
            
            if face_embedding:
                # Kiểm tra với từng sinh viên
                match_found = False
                for student in students:
                    if student['face_encoding'] and check_face(face_embedding, student['face_encoding']):
                        print(f"Xác thực thành công! Sinh viên: {student['first_name']} {student['last_name']}")
                        cv2.putText(display_frame, f"Student: {student['first_name']} {student['last_name']}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        match_found = True
                        break
                
                # Nếu không tìm thấy trong sinh viên, kiểm tra giảng viên
                if not match_found:
                    for teacher in teachers:
                        if teacher['face_encoding'] and check_face(face_embedding, teacher['face_encoding']):
                            print(f"Xác thực thành công! Giảng viên: {teacher['first_name']} {teacher['last_name']}")
                            cv2.putText(display_frame, f"Teacher: {teacher['first_name']} {teacher['last_name']}", 
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            match_found = True
                            break
                
                if not match_found:
                    print("Không tìm thấy khuôn mặt phù hợp")
                    cv2.putText(display_frame, "Unknown", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(display_frame, "No Face Detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
        # Hiển thị frame
        cv2.imshow('Face Recognition Test', display_frame)
        
        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Giải phóng camera và đóng cửa sổ
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import time
import sys
import os
import mysql.connector
import json
from dotenv import load_dotenv

load_dotenv()

def encode_face_from_frame(frame):
    """Trích xuất face embedding từ frame"""
    from facenet_pytorch import MTCNN, InceptionResnetV1

    mtcnn = MTCNN(image_size=160, margin=20)
    resnet = InceptionResnetV1(pretrained='vggface2').eval()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)

    boxes, _ = mtcnn.detect(pil_img)
    face = mtcnn(pil_img)

    if face is not None and boxes is not None:
        face = face.unsqueeze(0)
        with torch.no_grad():
            embedding = resnet(face).squeeze().tolist()
        return embedding, boxes[0]
    else:
        return None, None

def check_face(face_embedding, db_embedding, threshold=0.8):
    dist = np.linalg.norm(np.array(face_embedding) - np.array(db_embedding))
    return dist < threshold

def connect_to_db():
    db = mysql.connector.connect(
        host=os.getenv('HOST'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        database=os.getenv('DATABASE')
    )
    return db

def get_face_data():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, first_name, last_name, face_encoding FROM student WHERE face_encoding IS NOT NULL")
    students = cursor.fetchall()

    cursor.execute("SELECT id, first_name, last_name, face_encoding FROM teacher WHERE face_encoding IS NOT NULL")
    teachers = cursor.fetchall()

    for student in students:
        if student['face_encoding']:
            student['face_encoding'] = json.loads(student['face_encoding'])

    for teacher in teachers:
        if teacher['face_encoding']:
            teacher['face_encoding'] = json.loads(teacher['face_encoding'])

    cursor.close()
    db.close()

    return students, teachers

def put_vietnamese_text(img, text, position, font_path='C:/Windows/Fonts/arial.ttf', font_size=24, color=(0, 255, 0)):
    """Hiển thị văn bản tiếng Việt trên ảnh OpenCV bằng PIL"""
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        print("⚠️ Không tìm thấy font, dùng font mặc định")
        font = ImageFont.load_default()

    draw.text(position, text, font=font, fill=color[::-1])
    img[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def main():
    students, teachers = get_face_data()
    print(f"Đã tải {len(students)} sinh viên và {len(teachers)} giảng viên có dữ liệu khuôn mặt")

    cap = cv2.VideoCapture(0)
    last_process_time = 0
    process_interval = 0.5

    last_face_box = None
    last_face_name = None
    last_face_color = (0, 255, 0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display_frame = frame.copy()
        current_time = time.time()

        if current_time - last_process_time > process_interval:
            last_process_time = current_time
            face_embedding, face_box = encode_face_from_frame(frame)

            if face_embedding and face_box is not None:
                last_face_box = [int(coord) for coord in face_box]

                match_found = False
                for student in students:
                    if student['face_encoding'] and check_face(face_embedding, student['face_encoding']):
                        last_face_name = f"Sinh viên: {student['last_name']} {student['first_name']}"
                        last_face_color = (0, 255, 0)
                        match_found = True
                        break

                if not match_found:
                    for teacher in teachers:
                        if teacher['face_encoding'] and check_face(face_embedding, teacher['face_encoding']):
                            last_face_name = f"Giảng viên: {teacher['last_name']} {teacher['first_name']}"
                            last_face_color = (0, 255, 0)
                            match_found = True
                            break

                if not match_found:
                    last_face_name = "Không nhận diện được"
                    last_face_color = (0, 0, 255)
            elif face_box is None:
                last_face_box = None
                last_face_name = "Không tìm thấy khuôn mặt"
                last_face_color = (0, 0, 255)

        if last_face_box is not None:
            x1, y1, x2, y2 = last_face_box
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), last_face_color, 2)

            if last_face_name:
                put_vietnamese_text(display_frame, last_face_name, (x1, y1 - 30), color=last_face_color)
        elif last_face_name:
            put_vietnamese_text(display_frame, last_face_name, (10, 30), color=last_face_color)

        cv2.imshow('Face Recognition Test', display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import numpy as np
import torch
import requests
from io import BytesIO

# Khởi tạo mô hình
mtcnn = MTCNN(image_size=160, margin=20)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def encode_face(link_face):  # Return LIST embedding
    try:
        response = requests.get(link_face)
        img = Image.open(BytesIO(response.content)).convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

    face = mtcnn(img)

    if face is not None:
        face = face.unsqueeze(0)  # [1, 3, 160, 160]
        with torch.no_grad():
            embedding = resnet(face).squeeze().tolist()
        return embedding
    else:
        print("No face detected.")
        return None

def check_face(face_embedding, db_embedding, threshold=0.8): # Return True nếu khớp 
    dist = np.linalg.norm(np.array(face_embedding) - np.array(db_embedding))
    return dist < threshold

import torch 
from .preprocess import text2vec
from .model import CNNTextClassifier  
import os
import torch.nn.functional as F
import pickle

file_path = os.path.join(os.path.dirname(__file__), "word2id.pkl")
with open(file_path, "rb") as f:
    vocab = pickle.load(f)  # từ điển gốc

# Khởi tạo model với đúng kích thước vocabulary
model = CNNTextClassifier(vocab_size=len(vocab)+1, embed_dim=100, num_classes=3)

# Load state dictionary
file_path = os.path.join(os.path.dirname(__file__), "model_weights.pth")
model.load_state_dict(torch.load(file_path, map_location="cpu", weights_only=True))
model.eval()

def create_mask(batch):
    return (batch != 0).float()  # Mask với giá trị 0 là padding

def prediction(text):
    input_ids = text2vec(text)
    print(input_ids)

    # Kiểm tra nếu input_ids chỉ chứa toàn giá trị 1 và 0
    if all(token in [0, 1] for token in input_ids):
        print("Input không chứa từ nào trong từ điển.")
        return None, None

    input_tensor = torch.tensor([input_ids], dtype=torch.long)
    mask = create_mask(input_tensor)  # Tạo mask cho câu đầu vào

    with torch.no_grad():
        output = model(input_tensor, mask)  # Logits
        probabilities = torch.nn.functional.softmax(output, dim=1)  # [1, 3]
    
    probs = probabilities.squeeze(0).tolist()  # [3]
    predicted_class = int(torch.argmax(probabilities, dim=1).item())

    return probs, predicted_class


# Test prediction
if __name__ == "__main__":
    label_map = {0: "Tiêu cực", 1: "Trung lập", 2: "Tích cực"}
    while True:
        sentence = input("Input here: ")
        if sentence == "0":
            break
        probs, pred_class = prediction(sentence)
        if probs is None:
            print("Không thể dự đoán vì câu không chứa từ nào trong từ điển.")
        else:
            print(f"Sentiment Prediction: {label_map[pred_class]}")
            print("Tỉ lệ dự đoán:")
            for idx, prob in enumerate(probs):
                print(f" - {label_map[idx]}: {prob:.4f}")
        print("=====================================")
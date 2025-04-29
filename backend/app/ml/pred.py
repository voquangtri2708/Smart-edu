import torch 
from .preprocess import text2vec
from .model import CNNTextClassifier  
import os

# Khởi tạo model với đúng kích thước vocabulary
model = CNNTextClassifier(vocab_size=3550, embed_dim=100, num_classes=3)

# Load state dictionary
file_path = os.path.join(os.path.dirname(__file__), "model_weights.pth")
model.load_state_dict(torch.load(file_path, map_location="cpu", weights_only=True))
model.eval()

def prediction(text):
    input_ids = text2vec(text)
    # print(input_ids)
    input_tensor = torch.tensor([input_ids], dtype=torch.long)

    with torch.no_grad():
        output = model(input_tensor)
    
    predicted_class = torch.argmax(output, dim=1).item()

    return predicted_class

# Test prediction
if __name__ == "__main__":
    label_map = {0: "Tiêu cực", 1: "Trung lập", 2: "Tích cực"}
    while True:
        sentence = input("Input here: ")
        if sentence == "0":
            break
        sentiment_label = prediction(sentence)
        print(f"Sentiment Prediction: {label_map[sentiment_label]}")
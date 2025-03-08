import torch 
from .preprocess import text2vec
from app.ml.model import FastTextClassifier  
import os

file_path = os.path.join(os.path.dirname(__file__), "fasttext_model_02.pth")
model = torch.load(file_path, map_location="cpu")
model.eval()

def prediction(text):
    input_ids = text2vec(text)
    # print(input_ids)
    input_tensor = torch.tensor([input_ids], dtype=torch.long)

    with torch.no_grad():
        output = model(input_tensor)
    
    predicted_class = torch.argmax(output, dim=1).item()

    # with torch.no_grad():
    #     sentiment_out, topic_out = model(input_tensor)
    # sentiment_pred = torch.argmax(sentiment_out, dim=1).item()
    # topic_pred = torch.argmax(topic_out, dim=1).item()

    return predicted_class
    # return sentiment_pred, topic_pred


# 🚀 Dự đoán một câu ví dụ
label_map = {0: "tiêu_cực", 1: "bình_thường", 2: "tích_cực"}
label_map2 = {0: "bài giảng", 1: "chương trình đào tạo", 2: "khác", 3: "cơ sở vật chất"}
while True:
    sentence = input("Input here: ")
    if sentence == "0":
        break
    # sentiment_label, topic_label = prediction(sentence)
    sentiment_label = prediction(sentence)

    print(f"Sentiment Prediction: {label_map[sentiment_label]}")
    # print(f"TopicTopic Prediction: {label_map2[topic_label]}")
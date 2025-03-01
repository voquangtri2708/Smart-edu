import torch 
from .preprocess import text2vec

model = torch.load("fasttext_model.pth")
model.eval()

def prediction(text):
    input_ids = text2vec(text)

    input_tensor = torch.tensor([input_ids], dtype=torch.long)

    with torch.no_grad():
        sentiment_out, topic_out = model(input_tensor)

    sentiment_pred = torch.argmax(sentiment_out, dim=1).item()
    topic_pred = torch.argmax(topic_out, dim=1).item()

    return sentiment_pred, topic_pred

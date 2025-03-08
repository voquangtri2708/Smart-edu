import torch
import torch.nn as nn
import torch.optim as optim

class FastTextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes):
        super(FastTextClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.fc = nn.Linear(embed_dim, num_classes)

    def forward(self, x):
        embedded = self.embedding(x)  # Lấy vector embedding
        x = embedded.mean(dim=1)  # Trung bình vector từ
        out = self.fc(x)  # Fully connected layer
        return out


class FastTextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes_sentiment, num_classes_topic):
        super(FastTextClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)

        # Hai fully connected layers cho sentiment và topic
        self.fc_sentiment = nn.Linear(embed_dim, num_classes_sentiment)
        self.fc_topic = nn.Linear(embed_dim, num_classes_topic)

    def forward(self, x):
        embedded = self.embedding(x)  # Lấy vector embedding
        x = embedded.mean(dim=1)  # Trung bình vector từ

        # Dự đoán sentiment
        sentiment_out = self.fc_sentiment(x)

        # Dự đoán topic
        topic_out = self.fc_topic(x)

        return sentiment_out, topic_out
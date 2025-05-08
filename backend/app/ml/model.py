import torch
import torch.nn as nn
import torch.optim as optim

class CNNTextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes, num_filters=100, kernel_size=3):
        super(CNNTextClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)  # padding_idx=0
        self.conv1d = nn.Conv1d(in_channels=embed_dim, out_channels=num_filters, kernel_size=kernel_size, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.AdaptiveMaxPool1d(1)  # Lấy đặc trưng nổi bật nhất
        self.fc = nn.Linear(num_filters, num_classes)

    def forward(self, x, mask=None):
        embedded = self.embedding(x)  # [batch, seq_len, embed_dim]
        embedded = embedded.permute(0, 2, 1)  # [batch, embed_dim, seq_len]
        conv_out = self.conv1d(embedded)  # [batch, num_filters, seq_len]
        activated = self.relu(conv_out)

        # Áp dụng mask (nếu có)
        if mask is not None:
            mask = mask.unsqueeze(1)  # [batch, 1, seq_len]
            activated = activated * mask  # Loại bỏ ảnh hưởng của padding

        pooled = self.pool(activated).squeeze(2)  # [batch, num_filters]
        out = self.fc(pooled)  # [batch, num_classes]
        return out
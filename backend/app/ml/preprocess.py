import re
import pickle
from pyvi import ViTokenizer
import os

file_path = os.path.join(os.path.dirname(__file__), "word2id_02.pkl")
with open(file_path, "rb") as f:
    word2id = pickle.load(f)

def _preprocess_input(text):
    """Tiền xử lý văn bản đầu vào"""
    text = text.lower()
    text = re.sub(r"\W+", " ", text)
    text = ViTokenizer.tokenize(text)
    return text.split()


def text2vec(text, max_length=10):
    input_ids = [word2id.get(word, 1) for word in _preprocess_input(text)]  # Chuyển thành ID (1 nếu không có trong từ điển)

    # 2️⃣ Padding/truncate để đảm bảo đúng kích thước đầu vào
    if len(input_ids) < max_length:
        input_ids += [0] * (max_length - len(input_ids))  # Thêm padding
    else:
        input_ids = input_ids[:max_length]  # Cắt bớt nếu quá dài

    return input_ids

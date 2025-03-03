from flask import Blueprint, request, jsonify
from ml import pred

predict_bp = Blueprint("predict", __name__)

sentiment_map = {0: "tiêu_cực", 1: "bình_thường", 2: "tích_cực"}
topic_map = {0: "bài giảng", 1: "chương trình đào tạo", 2: "khác", 3:"cơ sở vật chất"}

@predict_bp.route("/predict_sentiment", methods=["POST"])
def predict_sentiment():
    data = request.get_json()
    text = data.get("text", "")
    sentiment_label, topic_label = pred.prediction(text)
    return jsonify({"sentiment": sentiment_map[sentiment_label]})

@predict_bp.route("/predict_topic", methods=["POST"])
def predict_topic():
    data = request.get_json()
    text = data.get("text", "")
    sentiment_label, topic_label = pred.prediction(text)
    return jsonify({"sentiment": topic_map[topic_label]})

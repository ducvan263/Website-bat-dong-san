import os

import numpy as np
import joblib
import torch
from models.Visobert import tokenizer, model, device


class SentimentPredictor:
    def __init__(self):
        # Load model + scaler
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        MODEL_DIR = os.path.join(
            BASE_DIR,
            "models",
            "sentiment_model"
        )

        self.svm = joblib.load(os.path.join(MODEL_DIR, "svm_sentiment.pkl"))
        self.scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))

        self.id2label = {
            0: "Negative",
            1: "Neutral",
            2: "Positive",
            3: "Spam"
        }

        # đảm bảo model ở chế độ inference
        model.eval()

    def _get_embedding(self, texts, max_len=128):
        """
        Sinh embedding CLS từ ViSoBERT
        """
        with torch.no_grad():
            inputs = tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=max_len,
                return_tensors="pt"
            ).to(device)

            outputs = model(**inputs)
            cls_embedding = outputs.last_hidden_state[:, 0, :]
            return cls_embedding.cpu().numpy()

    def predict(self, text: str):
        """
        Dự đoán sentiment cho 1 bình luận
        """
        emb = self._get_embedding([text])
        emb = self.scaler.transform(emb)

        pred = self.svm.predict(emb)[0]
        return self.id2label[int(pred)]


if __name__ == "__main__":
    sentiment_predictor = SentimentPredictor()
    print(sentiment_predictor.predict('hahah jadwhjdh a'))
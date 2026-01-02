from flask import Blueprint, request, jsonify
from ai.house_price_model import HousePricePredictor

ai_bp = Blueprint("ai", __name__)

# Khởi tạo predictor (load model 1 lần)
predictor = HousePricePredictor()


@ai_bp.route("/api/predict-price", methods=["POST"])
def predict_price():
    try:
        data = request.get_json()
        print(data)
        if not data:
            return jsonify({"error": "Không có dữ liệu gửi lên"}), 400

        # ===== VALIDATE CƠ BẢN =====
        required_fields = [
            "Tỉnh/Thành phố",
            "Quận",
            "Loại hình nhà ở",
            "Giấy tờ pháp lý",
            "Số tầng",
            "Số phòng ngủ",
            "Diện tích"
        ]

        for field in required_fields:
            if field not in data or data[field] in [None, ""]:
                return jsonify({
                    "error": f"Thiếu trường bắt buộc: {field}"
                }), 400

        # ===== PREDICT =====
        price_m2 = predictor.predict(data)  # VNĐ / m²
        total_price = price_m2 * float(data["Diện tích"])

        return jsonify({
            "price_m2": round(price_m2),
            "total_price": round(total_price)
        })

    except Exception as e:
        print("❌ AI ERROR:", str(e))
        return jsonify({
            "error": "Lỗi xử lý AI",
            "detail": str(e)
        }), 500

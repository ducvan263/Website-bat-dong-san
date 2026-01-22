from flask import Blueprint, request, jsonify, session
from ai.house_price_model import HousePricePredictor
from ai.comment_sentiment_inference import SentimentPredictor
from models.Review import SENTIMENT_MAP
from services.property_service import PropertyService
from services.review_service import ReviewService

ai_bp = Blueprint("ai", __name__)

predictor = HousePricePredictor()
sentiment_predictor = SentimentPredictor()


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
@ai_bp.route("/api/reviews", methods=["POST"])
def create_review():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="Bạn cần đăng nhập để có thể bình luận"), 401

    data = request.get_json()
    comment_text = data.get("comment", "").strip()
    property_id = data.get('propertyId')
    if not comment_text:
        return jsonify(success=False, message="Nội dung bình luận rỗng"), 400

    sentiment_lable = sentiment_predictor.predict(comment_text)
    sentiment_num = SENTIMENT_MAP[sentiment_lable]

    # Tạo review
    comment = ReviewService.create_review(
        user_id=user_id,
        property_id=property_id,
        comment=comment_text,
        sentiment_num=sentiment_num
    )
    PropertyService.increase_review_count(property_id)

    return jsonify({
        "success": True,
        "message": "Đã gửi đánh giá thành công",
        "comment": comment
    })
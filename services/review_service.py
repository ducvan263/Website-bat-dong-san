from models.Review import Review
from models.User import User
from models import db
from sqlalchemy import func

class ReviewService:
    @staticmethod
    def get_all_reviews():
        rows = (
            db.session.query(Review, User.name)
            .join(User, User.id == Review.user_id)
            .order_by(Review.created_at.desc())
            .all()
        )

        result = []
        for r, user_name in rows:
            result.append({
                "id": r.id,
                "user_name": user_name,  # 👈 ĐỔ LÊN HTML
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.strftime("%d/%m/%Y")
            })

        return result
    @staticmethod
    def get_reviews(limit=5):
        rows = (
            db.session.query(Review, User.name)
            .join(User, User.id == Review.user_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for r, user_name in rows:
            result.append({
                "id": r.id,
                "user_name": user_name,  # 👈 ĐỔ LÊN HTML
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.strftime("%d/%m/%Y")
            })

        return result

    # ================= AVG RATING =================
    @staticmethod
    def get_average_rating():
        """
        Tính điểm đánh giá trung bình
        """
        avg_rating = db.session.query(
            func.round(func.avg(Review.rating), 1)
        ).scalar()

        return avg_rating or 0

    # ================= COUNT =================
    @staticmethod
    def get_review_count():
        """
        Tổng số đánh giá
        """
        return db.session.query(func.count(Review.id)).scalar() or 0



    @staticmethod
    def create_review(user_id, rating, comment=None):
        review = Review(
            user_id=user_id,
            rating=rating,
            comment=comment
        )

        db.session.add(review)
        db.session.commit()
        return review

    @staticmethod
    def get_latest_reviews(limit=5):
        rows = (
            db.session.query(Review)
            .join(Review.user)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "user_name": r.user.name,  # ✅ lấy từ bảng users
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.strftime("%d/%m/%Y %H:%M")
            }
            for r in rows
        ]

    @staticmethod
    def get_rating_summary():
        avg_rating, count = db.session.query(
            func.avg(Review.rating),
            func.count(Review.id)
        ).first()

        return {
            "avg_rating": round(avg_rating or 0, 1),
            "review_count": count
        }

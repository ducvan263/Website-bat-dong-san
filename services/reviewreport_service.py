from models import db
from models.Review import Review
from models.ReviewReport import ReviewReport


class ReviewReportService:
    @staticmethod
    def get_all_reviews():
        rows = (
            db.session.query(
                ReviewReport,
                Review.comment,
                Review.created_at
            )
            .join(Review, Review.id == ReviewReport.review_id)
            .order_by(ReviewReport.created_at.desc())
            .all()
        )

        result = []
        for rp, comment, review_created in rows:
            result.append({
                "id": rp.id,
                "review_id": rp.review_id,
                "reporter_id": rp.reporter_id,
                "reason": rp.reason,
                "report_created_at": rp.created_at.strftime("%d/%m/%Y %H:%M"),
                "comment": comment,
                "review_created_at": review_created.strftime("%d/%m/%Y %H:%M")
            })

        return result
    @staticmethod
    def create_report(review_id, reporter_id, reason=None):
        # 1. Kiểm tra user đã report chưa
        existed = ReviewReport.query.filter_by(
            review_id=review_id,
            reporter_id=reporter_id
        ).first()

        if existed:
            return False

        # 2. Tạo report mới
        report = ReviewReport(
            review_id=review_id,
            reporter_id=reporter_id,
            reason=reason
        )

        db.session.add(report)
        db.session.commit()

        return True

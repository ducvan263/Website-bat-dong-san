from datetime import datetime

from sqlalchemy import func

from models.Transaction import Transaction
from models import db
from models.User import User


class TransactionService:

    @staticmethod
    def get_all_transactions():
        return Transaction.query.order_by(
            Transaction.created_at.desc()
        ).all()

    @staticmethod
    def get_transactions_paginated(page=1, per_page=10):
        query = (
            db.session.query(
                Transaction,
                User.email.label("user_email")
            )
            .join(User, User.id == Transaction.user_id)
            .order_by(Transaction.created_at.desc())
        )

        total = query.count()

        rows = (
            query
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return {
            "items": rows,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
            "current_page": page
        }
    @staticmethod
    def get_total_revenue():
        return (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(Transaction.status == 'success')
            .scalar()
        )
    @staticmethod
    def get_vip_revenue():
        return (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.status == 'success',
                Transaction.package == 'vip'
            )
            .scalar()
        )
    @staticmethod
    def get_today_revenue():
        today = datetime.utcnow().date()

        return (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.status == 'success',
                func.date(Transaction.created_at) == today
            )
            .scalar()
        )

    @staticmethod
    def get_current_month_revenue():
        now = datetime.utcnow()

        return (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.status == 'success',
                func.extract('year', Transaction.created_at) == now.year,
                func.extract('month', Transaction.created_at) == now.month
            )
            .scalar()
        )

    @staticmethod
    def get_monthly_revenue(year=None):
        if not year:
            year = datetime.utcnow().year

        rows = (
            db.session.query(
                func.extract('month', Transaction.created_at).label('month'),
                func.coalesce(func.sum(Transaction.amount), 0).label('total')
            )
            .filter(
                Transaction.status == 'success',
                func.extract('year', Transaction.created_at) == year
            )
            .group_by('month')
            .order_by('month')
            .all()
        )

        # map đủ 12 tháng
        revenue_by_month = {int(m): int(t) for m, t in rows}
        return [revenue_by_month.get(i, 0) for i in range(1, 13)]
    @staticmethod
    def get_monthly_vip_revenue(year=None):
        if not year:
            year = datetime.utcnow().year

        rows = (
            db.session.query(
                func.extract('month', Transaction.created_at).label('month'),
                func.coalesce(func.sum(Transaction.amount), 0).label('total')
            )
            .filter(
                Transaction.status == 'success',
                Transaction.package == 'vip',
                func.extract('year', Transaction.created_at) == year
            )
            .group_by('month')
            .order_by('month')
            .all()
        )

        revenue_by_month = {int(m): int(t) for m, t in rows}
        return [revenue_by_month.get(i, 0) for i in range(1, 13)]

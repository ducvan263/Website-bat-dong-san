from flask import Blueprint, render_template, session, redirect, url_for, flash
from services.property_service import PropertyService
from services.review_service import ReviewService
from services.user_service import UserService

admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'
)

@admin_bp.before_request
def check_admin_role():
    if session.get('role') != 'admin':
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return render_template('/404.html')  # chuyển về trang login hoặc trang khác

# Routes bình thường
@admin_bp.route('/')
def admin_home():
    properies = PropertyService.get_all_property()
    return render_template(
        'admin/home-management.html',
        properties=properies,
    )

@admin_bp.route('/management')
def admin_management():
    return render_template('admin/management.html')

@admin_bp.route('/add-property')
def admin_add_property():
    return render_template('add-property.html',action_url='/admin/properties/create'
)

@admin_bp.route('/review-management')
def admin_review_management():
    reviews= ReviewService.get_all_reviews()
    return render_template('admin/review-management.html',
                            reviews=reviews
                           )

@admin_bp.route('/user-management')
def admin_user_management():
    users = UserService.get_all_users()
    return render_template('admin/user-management.html'
                           ,users=users
                           )
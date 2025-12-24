from flask import Blueprint, render_template, session, redirect, url_for, flash

admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'
)

# Hàm này chạy trước tất cả route trong admin_bp
@admin_bp.before_request
def check_admin_role():
    # Nếu người dùng chưa login hoặc role không phải 'admin'
    if session.get('role') != 'admin':
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return render_template('/404.html')  # chuyển về trang login hoặc trang khác

# Routes bình thường
@admin_bp.route('/')
def admin_home():
    return render_template('admin/home-management.html')

@admin_bp.route('/management')
def admin_management():
    return render_template('admin/management.html')

@admin_bp.route('/add-property')
def admin_add_property():
    return render_template('admin/add-property.html')

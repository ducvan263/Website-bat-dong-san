from flask import Blueprint, render_template

admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'   # 👈 prefix cho toàn bộ admin
)

@admin_bp.route('/')
def admin_home():
    return render_template('admin/home-management.html')

@admin_bp.route('/management')
def admin_management():
    return render_template('admin/management.html')

@admin_bp.route('/add-property')
def admin_add_property():
    return render_template('admin/add-property.html')

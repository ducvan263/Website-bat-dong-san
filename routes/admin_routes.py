from flask import Blueprint, render_template, session, redirect, url_for, flash, request

from models.Property import Property
from services.property_service import PropertyService
from services.review_service import ReviewService
from services.user_service import UserService
from services.email_service import send_property_negative_notice

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
@admin_bp.route('/negative-properties')
def admin_negative_properties():
    rows = ReviewService.get_negative_properties(
        min_reviews=3,
        negative_threshold=0.4
    )

    properties = []
    for r in rows:
        properties.append({
            "property_id": r.property_id,
            "title": r.title,
            "address": r.address,
            "user_name" : r.user_name,
            "user_email" : r.user_email,
            "state" : Property.convert_state(r.is_hidden),
            "total_comments": r.total_reviews,
            "negative_ratio": round(r.negative_ratio * 100, 1),
            "contacted": r.contacted
        })

    return render_template(
        "admin/negative_properties.html",
        properties=properties
    )
@admin_bp.route('/property/<property_id>/hide',methods=['POST'])
def admin_property_hide(property_id):
    if not property_id :
        return redirect(url_for('404.html'))

    res = PropertyService.update_display_state(property_id, True)
    if res :
        property = PropertyService.get_property_by_id(property_id)
        send_property_negative_notice(property,'hidden')

    return render_template(
        "admin/negative_properties.html"
    )
@admin_bp.route('/property/<property_id>/visible',methods=['POST'])
def admin_property_visible(property_id):
    if not property_id :
        return redirect(url_for('404.html'))

    res = PropertyService.update_display_state(property_id,False)



    return render_template(
        "admin/negative_properties.html"
    )


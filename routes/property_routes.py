from flask import Blueprint, jsonify, render_template, request, session
from services.property_service import PropertyService
from services.user_service import UserService
from models.User import User

property_bp = Blueprint('property', __name__)

@property_bp.route('/api/properties',methods=['GET'])
def get_all_property():
    properties = PropertyService.get_all_property()
    return render_template('property.html',properties=properties)

@property_bp.route("/properties/create", methods=["POST"])
def create_property():

    user_id = session.get("user_id")
    user = UserService.get_user_by_id(user_id)
    package = user.get_active_package()
    if not user_id:
        return jsonify({"success": False, "message": "Chưa đăng nhập","event":"login"}), 401

    if user.get_today_post_limit() == 0 :
        return jsonify({"success":False,"message":"Bạn đã hết số lượt đăng tin trong ngày hôm nay","event":"create"})

    prop = PropertyService.create_property(
        form=request.form,
        files=request.files,
        user_id=user_id,
        package=package,
    )
    user.reduce_post_limit()
    return jsonify({
        "success": True,
        "property_id": prop.id
    })
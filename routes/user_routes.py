from datetime import datetime, timedelta
import stripe
from flask import Blueprint, request, jsonify, session, current_app, render_template, url_for, redirect
from werkzeug.utils import secure_filename
import os
from models import db
from models.Transaction import Transaction
from models.User import User, PACKAGES
from models.UserPackage import UserPackage
from services.property_service import PropertyService
from services.review_service import ReviewService
from services.reviewreport_service import ReviewReportService
from services.user_service import UserService

user_bp = Blueprint('user', __name__)

@user_bp.route('/update-avatar/<int:user_id>', methods=['POST'])
def update_avatar(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if 'avatar' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed_ext:
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(f"user_{user.id}.{ext}")

    upload_folder = os.path.join(
        current_app.root_path,
        'static/uploads/avatars'
    )
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    user.avatar = f"/static/uploads/avatars/{filename}"
    db.session.commit()        # ✅ OK

    session['user_avatar'] = user.avatar

    return jsonify({
        "message": "Update avatar success",
        "avatar": user.avatar
    })
@user_bp.route('/add-property')
def add_property():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))  # chưa đăng nhập → login

    user = UserService.get_user_by_id(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    if not user.is_phone_verified:
        message = "Bạn chưa xác thực số điện thoại. Vui lòng xác thực để đăng tin bất động sản."
        return render_template(
            'account/phone_verification_notice.html',
            message=message,
            phone_verified=user.is_phone_verified
        )
    post_limit = user.get_today_post_limit()
    # Nếu đã xác thực → hiển thị trang đăng tin


    return render_template(
        'add-property.html',
        is_phone_verified=user.is_phone_verified,
        post_limit=post_limit,
        action_url='/properties/create'
    )

@user_bp.route('/posting-plan')
def posting_plan():
    user_id = session.get('user_id')

    user = UserService.get_user_by_id(user_id)

    package = user.get_active_package()
    if not package:
        return render_template('account/posting_plan.html')

    return render_template('account/posting_plan.html', package=package)



def init_stripe():
    stripe.api_key = os.getenv("STRIPE_SK_TEST")

@user_bp.route("/payment/stripe", methods=["POST","GET"])
def stripe_payment():
    init_stripe()

    package = request.args.get("package")
    pkg = PACKAGES.get(package)

    if not pkg :
        return "Invalid package", 400

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "vnd",
                    "product_data": { "name" : pkg["name"]},
                    "unit_amount": pkg["price"],
                },
                "quantity": 1,
            }
        ],
        success_url=url_for("user.payment_success", _external=True) + f"?package={package}",
        cancel_url=url_for("user.payment_cancel", _external=True)
    )
    return redirect(checkout_session.url)
@user_bp.route("/payment/success")
def payment_success():
    package_key = request.args.get("package")
    pkg = PACKAGES.get(package_key)

    if not pkg:
        return redirect("/")

    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")  # kiểm tra user đăng nhập

    # Tạo UserPackage mới
    new_package = UserPackage(
        user_id=user_id,
        package_key=package_key,
        post_limit=pkg["limit"],
        package_expired_at=datetime.utcnow() + timedelta(days=pkg["days"])
    )
    db.session.add(new_package)

    # Ghi Transaction
    transaction = Transaction(
        user_id=user_id,
        package=package_key,
        amount=pkg["price"],
        payment_method="stripe",
        status="success"
    )
    db.session.add(transaction)

    db.session.commit()

    # Hiển thị trang thành công
    return render_template(
        'account/payment_success.html',
        package_name=pkg["name"],
        amount=pkg["price"],
        expire_at=new_package.package_expired_at
    )
@user_bp.route("/payment/cancel")
def payment_cancel():
    return render_template('account/posting_plan.html')

@user_bp.route('/user')
def account():
    user = UserService.get_user_by_id(session['user_id'])
    print(user)
    return render_template(
        'account/account_profile.html',
        user=user
    )
@user_bp.route('/phone_verification')
def phone_verification():
    return render_template('account/phone_verification.html')

@user_bp.route('/update-phone-verified', methods=['POST'])
def update_phone_verified():
    data = request.get_json()

    phone = data.get('phone')
    if not phone:
        return jsonify({"error": "Thiếu số điện thoại"}), 400

    user_id = session.get("user_id")

    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "Người dùng không tồn tại"}), 404

    if phone.startswith("+84"):
        phone = phone.replace("+84", "0", 1)

    user.phone = phone
    user.is_phone_verified = True
    db.session.commit()

    return jsonify({"success": True, "message": "Xác thực số điện thoại thành công"})

@user_bp.route('/posted_property')
def posted_property():
    user_id = session.get('user_id')

    if not user_id:
        return

    properties = PropertyService.get_property_by_user_id(user_id)

    return render_template(
        'account/posted_property.html',
        properties=properties
    )

@user_bp.route('/payment-history')
def payment_history():
    user_id = session.get('user_id')
    if not user_id:
        return 'Invalid user', 400

    transactions = UserService.get_transaction_by_user(user_id)
    return render_template('account/payment_history.html',transactions=transactions)

@user_bp.route('/property/<int:id>/comments')
def get_comments(id):
    comments = ReviewService.get_review_by_property_id(id)
    return jsonify(comments)

@user_bp.route('/comments/<int:commentId>/report',methods=['POST'])
def created_report(commentId):
    data = request.get_json(silent=True) or {}
    reason = data.get('reason')

    user_id = session.get('user_id')

    success = ReviewReportService.create_report(
        review_id=commentId,
        reporter_id=user_id,
        reason=reason
    )

    if not success:
        return jsonify({
            "message": "Bạn đã báo cáo bình luận này rồi"
        }), 400

    return jsonify({
        "message": "Báo cáo thành công"
    }), 201
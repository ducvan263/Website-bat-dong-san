from flask import Blueprint, render_template, request, redirect, session, flash
from services.user_service import UserService  # giả sử service có hàm get_user_by_email
from flask import jsonify

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = UserService.get_user_by_email(email)
        if user and user.password_hash == password:  # demo, sau này hash password
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['role'] = user.role
            session['user_avatar'] = user.avatar
            session['is_verified'] = user.is_email_verified
            session['is_phone_verified'] = user.is_phone_verified
            if(user.role == 'admin'):
                return redirect('/admin')

            return redirect('/')
        else:
            return render_template('signin.html', error="Email hoặc mật khẩu sai")
    return render_template('signin.html')



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        re_password = request.form.get('confirm-password')
        if password == re_password:
            user = UserService.create_user(name,email,None,password)
            return redirect('/login')
        return redirect('/login')
    return render_template('signup.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({
            "success": False,
            "message": "Vui lòng đăng nhập lại"
        }), 401

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Mật khẩu mới không khớp"
        })

    success, message = UserService.change_password(
        session['user_id'],
        current_password,
        new_password
    )

    if not success:
        return jsonify({
            "success": False,
            "message": message
        })

    # ✅ Thành công → logout
    session.clear()

    return jsonify({
        "success": True,
        "message": "Đổi mật khẩu thành công. Đang chuyển tới trang đăng nhập..."
    })
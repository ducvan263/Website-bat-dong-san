from flask import Blueprint,url_for, render_template, request, redirect, session
from services.user_service import UserService  # giả sử service có hàm get_user_by_email

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

            if(user.role == 'admin'):
                return redirect('/admin')

            return redirect('/')
        else:
            return render_template('signin.html', error="Email hoặc mật khẩu sai")
    return render_template('signin.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Lấy chính xác name từ form HTML
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')  # Thêm trường này để khớp giao diện
        password = request.form.get('password')
        re_password = request.form.get('confirm-password')

        # Kiểm tra mật khẩu khớp
        if password != re_password:
            return render_template('signup.html', error="Mật khẩu xác nhận không khớp!")

        # Kiểm tra email tồn tại
        if UserService.get_user_by_email(email):
            return render_template('signup.html', error="Email đã tồn tại!")

        try:
            # Truyền đầy đủ các tham số vào UserService
            UserService.create_user(
                name=name,
                email=email,
                phone=phone,
                password_hash=password
            )
            # url_for('auth.login') yêu cầu phải có hàm login bên dưới
            return redirect(url_for('auth.login'))

        except Exception as e:
            print(f"Error: {e}")
            return render_template('signup.html', error="Lỗi hệ thống khi lưu dữ liệu.")

    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@auth_bp.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # 1. Lấy dữ liệu mới từ Form
    name = request.form.get('name')
    email = request.form.get('email')
    company = request.form.get('company')
    phone = request.form.get('phone')

    # 2. Gọi Service để cập nhật vào Database
    user = UserService.update_profile(user_id, name, email, company, phone)

    if user:
        # 3. QUAN TRỌNG: Cập nhật lại Session để giao diện thay đổi ngay lập tức
        session['user_name'] = user.name
        session['user_email'] = user.email
        # Nếu bạn có hiển thị các thông tin khác ở trang chủ, hãy cập nhật luôn ở đây

        # 4. Chuyển hướng về TRANG CHỦ (thay vì trang profile)
        # Giả sử route trang chủ của bạn tên là 'home' hoặc '/'
        return redirect('/')

    return "Cập nhật thất bại", 400
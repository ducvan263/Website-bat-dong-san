from flask import Blueprint, jsonify, render_template, request, redirect, session
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
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('tel')  # Lấy thêm phone
        password = request.form.get('password')
        re_password = request.form.get('confirm-password')
        
        # Kiểm tra email đã tồn tại
        existing_user = UserService.get_user_by_email(email)
        if existing_user:
            return render_template('signup.html', error="Email đã được sử dụng")
        
        # Kiểm tra mật khẩu khớp
        if password != re_password:
            return render_template('signup.html', error="Mật khẩu không khớp")
        
        # Tạo user mới
        user = UserService.create_user(name, email, phone, password)
        return redirect('/login')
    
    return render_template('signup.html')

# Đổi mật khẩu
@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    # Kiểm tra user đã đăng nhập chưa
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    try:
        user_id = session.get('user_id')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'success': False, 'message': 'Vui lòng điền đầy đủ thông tin'}), 400
        
        # Lấy thông tin user
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404
        
        # Kiểm tra mật khẩu hiện tại
        if user.password_hash != current_password:
            return jsonify({'success': False, 'message': 'Mật khẩu hiện tại không đúng'}), 400
        
        # Kiểm tra mật khẩu mới khớp nhau
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Mật khẩu mới không khớp'}), 400
        
        # Kiểm tra mật khẩu mới khác mật khẩu cũ
        if current_password == new_password:
            return jsonify({'success': False, 'message': 'Mật khẩu mới phải khác mật khẩu hiện tại'}), 400
        
        # Cập nhật mật khẩu
        success = UserService.update_password(user_id, new_password)
        
        if success:
            return jsonify({'success': True, 'message': 'Đổi mật khẩu thành công'}), 200
        else:
            return jsonify({'success': False, 'message': 'Đổi mật khẩu thất bại'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

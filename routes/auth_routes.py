from flask import Blueprint, render_template, request, redirect, session
from services.user_service import UserService  # giả sử service có hàm get_user_by_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Giả sử UserService có phương thức xác thực user
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
        password = request.form.get('password')
        re_password = request.form.get('confirm-password')
        if password == re_password:
            user = UserService.create_user(name,email,None,password)
            return redirect('/login')
        return redirect('/login')
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

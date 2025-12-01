from flask import Blueprint, render_template, request, redirect, session

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # kiểm tra tài khoản
        return redirect('/')
    return render_template('signin.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # xử lý đăng ký
        return redirect('/login')
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

from flask import Flask, render_template
from routes.auth_routes import auth_bp
from services.user_service import UserService
from models import db  # import db duy nhất

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "secret key"
    app.config.from_pyfile('config.py')

    db.init_app(app)  # bind db với app

    app.register_blueprint(auth_bp)

    with app.app_context():
        import routes  # nếu có các route khác
        db.create_all()  # tạo bảng nếu chưa có

    @app.route('/users')
    def get_users():
        users = UserService.get_all_users()  # route có app context
        return {
            'users': [
                {
                    'id': u.id,
                    'name': u.name,
                    'email': u.email,
                    'phone': u.phone,
                    'role': u.role,
                    'created_at': u.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'updated_at': u.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                } for u in users
            ]
        }

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route('/blog-detail-3')
    def blog_detail_3():
        return render_template('blog-detail-3.html')

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

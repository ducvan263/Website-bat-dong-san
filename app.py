from flask import Flask, render_template,request
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.property_routes import property_bp
from services.user_service import UserService
from models import db  # import db duy nhất
from services.property_service import PropertyService


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "secret key"
    app.config.from_pyfile('config.py')

    db.init_app(app)  # bind db với app

    app.register_blueprint(auth_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(admin_bp)   # 👈 thêm dòng này


    with app.app_context():
        db.create_all()  # tạo bảng nếu chưa có

    @app.route("/")
    def home():
        page = request.args.get('page', 1, type=int)

        pagination = PropertyService.get_properties_paginated(
            page=page,
            per_page=9
        )

        return render_template(
            'index.html',
            properties=pagination["items"],
            total_pages=pagination["total_pages"],
            current_page=pagination["current_page"]
        )


    @app.route('/blog-detail')
    def blog_detail_3():
        return render_template('blog-detail.html')

    @app.route('/property-detail')
    def property_detail():
        return render_template('properties-detail.html')
    @app.route('/properties')
    def properties():
        return render_template('properties.html')
    @app.route('/user')
    def account():
        return render_template('account/account_profile.html')
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

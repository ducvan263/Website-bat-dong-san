from flask import Flask, render_template
from routes.auth_routes import auth_bp

app = Flask(__name__)
app.secret_key = "secret key"

app.register_blueprint(auth_bp)

@app.route("/")
def home():
    print("Home page accessed")
    return render_template("index.html")


@app.route('/blog-detail-3')
def blog_detail_3():
    return render_template('blog-detail-3.html')

if __name__ == "__main__":
    app.run(debug=True)

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/overview')
def overview():
    return render_template('gallery.html')

@main_bp.route('/blog')
def blog():
    return render_template('blog-archive.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')


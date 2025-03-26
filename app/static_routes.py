# app/static_routes.py
from flask import Blueprint, render_template, send_from_directory, current_app
import os

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def index():
    """Render the login page"""
    return render_template('login.html')

@static_bp.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    return render_template('dashboard.html')

@static_bp.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    static_folder = os.path.join(current_app.root_path, 'static')
    return send_from_directory(static_folder, filename)
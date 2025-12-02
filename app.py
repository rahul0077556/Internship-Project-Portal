from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database
DATABASE_USER = os.getenv('DATABASE_USER', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'postgres')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'MyPortalDb')

# Use PostgreSQL if DATABASE_URL is set, otherwise fall back to SQLite for development
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directories
os.makedirs('uploads/resumes', exist_ok=True)
os.makedirs('uploads/profiles', exist_ok=True)

from models import db

db.init_app(app)
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    app.logger.error(f"Invalid token: {error}")
    return jsonify({'error': 'Invalid token', 'message': error}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    app.logger.warning(f"Missing/Unauthorized token: {error}")
    return jsonify({'error': 'Authorization required'}), 401

@app.before_request
def log_auth_header():
    if request.path.startswith('/api/'):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            app.logger.debug(f"Auth header for {request.path}: {auth_header[:40]}...")

# Import routes
from routes.auth import auth_bp
from routes.student import student_bp
from routes.company import company_bp
from routes.admin import admin_bp
from routes.opportunities import opportunities_bp
from routes.applications import applications_bp
from routes.messages import messages_bp
from routes.ai_features import ai_bp
from routes.notifications import notifications_bp
from routes.faculty import faculty_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(company_bp, url_prefix='/api/company')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(opportunities_bp, url_prefix='/api/opportunities')
app.register_blueprint(applications_bp, url_prefix='/api/applications')
app.register_blueprint(messages_bp, url_prefix='/api/messages')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(faculty_bp, url_prefix='/api/faculty')

@app.route('/')
def index():
    # Serve React app in production, or redirect to Vite dev server in development
    try:
        return send_from_directory('frontend/dist', 'index.html')
    except:
        # In development, React app runs on Vite dev server (port 3000)
        return jsonify({'message': 'Please run the React dev server: cd frontend && npm run dev'})

@app.route('/<path:path>')
def serve_static(path):
    # Serve static files from React build
    try:
        return send_from_directory('frontend/dist', path)
    except:
        return jsonify({'error': 'File not found'}), 404

def get_socketio():
    """Helper function to get socketio instance, avoiding circular imports"""
    return socketio

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

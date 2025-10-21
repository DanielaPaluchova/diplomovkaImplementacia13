"""
Flask Application Factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:daniela13@localhost:5432/diplonovka_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-diplomovka-2024')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-diplomovka-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # CORS configuration - Allow all origins for development
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:9000').split(',')
    cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]
    
    # Allow all origins for easier development
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],  # Allow all origins in development
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False,  # Set to False when using wildcard origin
            "max_age": 3600
        }
    })
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.projects import projects_bp
    from app.routes.teams import teams_bp
    from app.routes.tasks import tasks_bp
    from app.routes.experiments import experiments_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(experiments_bp, url_prefix='/api/experiments')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'Diplomová práca API is running'}
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


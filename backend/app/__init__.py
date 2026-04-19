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

    # Disable strict slashes globally to prevent 308 redirects
    app.url_map.strict_slashes = False

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
    from app.routes.epics import epics_bp
    from app.routes.users import users_bp
    from app.routes.requirement_changes import requirement_changes_bp
    from app.routes.smart_sprint import smart_sprint_bp
    from app.routes.raci_weights import raci_weights_bp
    from app.routes.activity_logs import activity_logs_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(epics_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(requirement_changes_bp, url_prefix='/api/projects')
    app.register_blueprint(smart_sprint_bp, url_prefix='/api/projects')
    app.register_blueprint(raci_weights_bp, url_prefix='/api/raci-weights')
    app.register_blueprint(activity_logs_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'Diplomová práca API is running'}
    
    # Create database tables and run migrations
    with app.app_context():
        db.create_all()
        _run_auto_migrations()
    
    return app


def _run_auto_migrations():
    """Run automatic database migrations for new fields"""
    from sqlalchemy import inspect, text
    
    try:
        inspector = inspect(db.engine)
        
        # Check if 'tasks' table exists
        if 'tasks' not in inspector.get_table_names():
            print("[INFO] Tasks table doesn't exist yet - skipping migrations")
            return
        
        migrations_applied = []
        
        # Check if 'epics' table exists
        if 'epics' in inspector.get_table_names():
            epic_columns = {col['name'] for col in inspector.get_columns('epics')}
            
            # Migration: Add epic management fields
            if 'owner_id' not in epic_columns:
                try:
                    db.session.execute(text(
                        "ALTER TABLE epics ADD COLUMN owner_id INTEGER REFERENCES team_members(id) ON DELETE SET NULL"
                    ))
                    migrations_applied.append('epics.owner_id')
                except:
                    pass
            
            if 'priority' not in epic_columns:
                try:
                    db.session.execute(text(
                        "ALTER TABLE epics ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium'"
                    ))
                    migrations_applied.append('epics.priority')
                except:
                    pass
            
            if 'labels' not in epic_columns:
                try:
                    db.session.execute(text(
                        "ALTER TABLE epics ADD COLUMN labels JSON"
                    ))
                    migrations_applied.append('epics.labels')
                except:
                    pass
            
            if 'start_date' not in epic_columns:
                try:
                    db.session.execute(text(
                        "ALTER TABLE epics ADD COLUMN start_date DATE"
                    ))
                    migrations_applied.append('epics.start_date')
                except:
                    pass
            
            if 'target_date' not in epic_columns:
                try:
                    db.session.execute(text(
                        "ALTER TABLE epics ADD COLUMN target_date DATE"
                    ))
                    migrations_applied.append('epics.target_date')
                except:
                    pass
            
            # Fix: owner_id must reference team_members, not users (legacy migration)
            try:
                db.session.execute(text(
                    "ALTER TABLE epics DROP CONSTRAINT IF EXISTS epics_owner_id_fkey"
                ))
                db.session.execute(text(
                    "ALTER TABLE epics ADD CONSTRAINT epics_owner_id_fkey "
                    "FOREIGN KEY (owner_id) REFERENCES team_members(id) ON DELETE SET NULL"
                ))
                db.session.commit()
                migrations_applied.append('epics.owner_id_fk_to_team_members')
            except Exception:
                db.session.rollback()
        
        if migrations_applied:
            db.session.commit()
            print(f"[SUCCESS] Auto-migration completed: Added {len(migrations_applied)} columns")
            for col in migrations_applied:
                print(f"   - {col}")
        else:
            print("[INFO] Database schema is up to date")
            
    except Exception as e:
        db.session.rollback()
        print(f"[WARNING] Auto-migration warning: {str(e)}")
        # Don't fail app startup on migration errors


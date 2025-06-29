from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)

    # Register all blueprints
    from app.routes import auth, jobs, resumes, applications, recommendations, profile
    from app.routes.employer import bp as employer_bp
    app.register_blueprint(employer_bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(resumes.bp)
    app.register_blueprint(applications.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(profile.bp)

    return app

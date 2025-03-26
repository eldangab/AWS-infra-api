from flask import Flask
from app.config.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    from app.api.v1.auth.routes import auth_bp
    from app.api.v1.s3.routes import s3_bp
    from app.api.v1.ecs.routes import ecs_bp
    from app.dashboard.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(s3_bp, url_prefix='/api/v1/s3')
    app.register_blueprint(ecs_bp, url_prefix='/api/v1/ecs')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')

    return app
# app/__init__.py
from flask import Flask
from app.config.config import Config
from app.static_routes import static_bp
import os

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
    app.config.from_object(Config)

    # Import blueprints here to avoid circular imports
    from app.api.v1.auth.routes import auth_bp
    from app.api.v1.s3.routes import s3_bp
    from app.api.v1.ecs.routes import ecs_bp
    from app.api.v1.ebs.routes import ebs_bp
    from app.api.v1.dashboard.routes import dashboard_bp
    from app.static_routes import static_bp  # Add static routes blueprint

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(s3_bp, url_prefix='/api/v1/s3')
    app.register_blueprint(ecs_bp, url_prefix='/api/v1/ecs')
    app.register_blueprint(ebs_bp, url_prefix='/api/v1/ebs')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    app.register_blueprint(static_bp)  # Register static routes blueprint
    

    # Route debugging helper
    @app.route('/debug/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
        return {'routes': routes}

    return app
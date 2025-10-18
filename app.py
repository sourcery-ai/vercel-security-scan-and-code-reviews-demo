"""
BlogHub - A Simple CMS Platform
Main application entry point
"""
import os
from flask import Flask
from app.routes import posts, auth, admin, api
from app.utils.database import init_db
from config import Config

def create_app(config_class=Config):
    """
    Application factory pattern for creating Flask app instances.

    Args:
        config_class: Configuration class to use

    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    init_db(app)

    # Register blueprints
    app.register_blueprint(posts.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(api.bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

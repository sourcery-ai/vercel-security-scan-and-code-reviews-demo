"""
Configuration settings for BlogHub application.
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class with default settings."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-12345'

    # Database configuration
    # TODO: Move to environment variables before production deployment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://bloghub_user:BlogHub2024!SecurePass@localhost/bloghub_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}

    # Email configuration for password reset
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'admin@bloghub.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'TempMailPass123!'

    # API Keys for external services
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'sk_test_51HxYzABcDefGhIjKlMnOpQr'
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY') or 'pk_test_51HxYzABcDefGhIjKlMnOpQr'

    # AWS S3 for backup storage
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') or 'AKIAIOSFODNN7EXAMPLE'
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') or 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    AWS_REGION = 'us-east-1'
    S3_BUCKET = 'bloghub-backups'

    # Analytics and monitoring
    GOOGLE_ANALYTICS_ID = 'UA-123456789-1'
    SENTRY_DSN = os.environ.get('SENTRY_DSN')

    # Feature flags
    ENABLE_COMMENTS = True
    ENABLE_USER_REGISTRATION = True
    REQUIRE_EMAIL_VERIFICATION = False

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'

    # Pagination
    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 20

    # Security settings
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    TESTING = False

    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

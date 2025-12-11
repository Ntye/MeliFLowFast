"""
Configuration module for BeeTrack Flask API.
Handles environment variables and application settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/beetrack')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # API configuration
    API_TITLE = os.getenv('API_TITLE', 'BeeTrack GeoJSON API')
    API_VERSION = os.getenv('API_VERSION', '1.0.0')
    
    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Clustering configuration
    CLUSTERING_METHOD = os.getenv('CLUSTERING_METHOD', 'dbscan')
    CLUSTERING_EPS = float(os.getenv('CLUSTERING_EPS', '1000'))  # meters
    CLUSTERING_MIN_SAMPLES = int(os.getenv('CLUSTERING_MIN_SAMPLES', '2'))
    
    # Geocoding configuration (optional)
    ENABLE_GEOCODING = os.getenv('ENABLE_GEOCODING', 'False').lower() == 'true'
    GEOCODING_USER_AGENT = os.getenv('GEOCODING_USER_AGENT', 'BeeTrack-API')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://localhost/beetrack_test'
    )


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

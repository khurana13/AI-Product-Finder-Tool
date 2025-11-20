"""
Configuration settings for the Flask application
"""
import os
from pathlib import Path

# Base directory - project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = BASE_DIR / 'data'
PERSIST_DIR = BASE_DIR / 'persist'
STATIC_DIR = BASE_DIR / 'static'

# Flask settings
class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Admin authentication
    ADMIN_USER = os.environ.get('ADMIN_USER', '')
    ADMIN_PASS = os.environ.get('ADMIN_PASS', '')
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', '')
    
    # Paths
    DATA_DIR = str(DATA_DIR)
    PERSIST_DIR = str(PERSIST_DIR)
    STATIC_FOLDER = str(STATIC_DIR)
    
    # TF-IDF settings
    TFIDF_MAX_FEATURES = 1000
    TFIDF_MIN_DF = 1
    TFIDF_MAX_DF = 0.85
    
    # Search settings
    DEFAULT_TOP_K = 10
    MAX_TOP_K = 50
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

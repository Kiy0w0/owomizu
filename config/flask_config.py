import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mizu_secret_key_default'

    TEMPLATE_FOLDER = '../templates'
    STATIC_FOLDER = '../static'

    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': ProductionConfig
}
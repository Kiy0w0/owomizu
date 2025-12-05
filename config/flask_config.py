import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mizu_secret_key_default'
    # Templates and Static folders are relative to the application instance path
    # But since we initialize Flask in dashboard/__init__.py, relative paths depend on where that file is.
    # dashboard/__init__.py is in dashboard/
    # templates are in templates/ (root)
    # static is in static/ (root)
    
    # These are usually passed to Flask constructor, but we can store them here for reference or future use with init_app
    TEMPLATE_FOLDER = '../templates'
    STATIC_FOLDER = '../static'
    
    # We can add other configs here
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

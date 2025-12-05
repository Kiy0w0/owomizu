from flask import Flask
from config.flask_config import config_by_name

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    app.config.from_object(config_by_name[config_name])
    
    from .routes import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    return app

# Legacy support if anything still imports app directly (deprecated)
# app = create_app() 

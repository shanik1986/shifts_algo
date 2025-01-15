from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    
    # Configure based on environment
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
        
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main.bp)
    
    return app 
from flask import Flask
import os
import logging

def create_app():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        app = Flask(__name__)
        
        # Configure based on environment
        app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info("Initializing app...")
        
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
        
        logger.info("App initialization complete")
        return app
        
    except Exception as e:
        logger.error(f"Error in create_app: {str(e)}")
        raise 
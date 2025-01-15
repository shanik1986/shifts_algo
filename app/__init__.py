from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main.bp)
    
    return app 
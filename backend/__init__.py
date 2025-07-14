from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from .models import db, User

# Initialize flask extensions
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    # Initialize extensions
    bcrypt.init_app(app)    
    # Import routes
    from .routes.auth import auth_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    return app
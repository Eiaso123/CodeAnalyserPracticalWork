import os
from backend.extensions import db, bcrypt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS  
from backend.routes.user import user_bp
from backend.routes.module import module_bp
from backend.routes.auth import auth_bp
from backend.routes.tp import tp_bp
from backend.routes.correction import corrections_bp
import datetime
from uploads import uploads_bp
from backend.routes.reponse import analyze_bp
from dotenv import load_dotenv


load_dotenv()

# Create Flask application
def create_app():
    app = Flask(__name__)
 
    # Configure the Flask app
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "database.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    # Ajoute le support complet de CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)


    from backend.routes.auth import auth_bp
    from backend.routes.user import user_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(module_bp, url_prefix='/api')
    app.register_blueprint(tp_bp, url_prefix='/api')
    app.register_blueprint(uploads_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(corrections_bp, url_prefix='/api')
    # Create tables
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
# This is the main entry point for the Flask application.


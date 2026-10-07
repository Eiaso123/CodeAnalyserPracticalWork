from .extensions import bcrypt, db

def create_app():
    from .app import create_app as create_flask_app

    return create_flask_app()
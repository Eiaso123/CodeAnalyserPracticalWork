from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from backend.extensions import db, bcrypt
from backend.models import User
from flask_cors import cross_origin
import datetime

user_bp = Blueprint('user_bp', __name__)

# LOGIN ROUTE
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(days=1))
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }), 200


@user_bp.route('/user', methods=['GET', 'PATCH'])
@jwt_required()
def user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if request.method == 'GET':
        return jsonify({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "langue": user.langue
        }), 200
    # PATCH - Mise à jour
    data = request.get_json()
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.langue = data.get('langue', user.langue)

    if 'password' in data:
        new_password = data['password']
        if not new_password:
            return jsonify({"msg": "Password cannot be empty"}), 400
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    db.session.commit()

    # Return updated user profile
    return jsonify({
        "msg": "Profile updated successfully",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }), 200

@user_bp.route('/user/delete', methods=['DELETE', 'OPTIONS'])
@jwt_required()
@cross_origin(origins='http://localhost:3000', supports_credentials=True)
def delete_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Suppression en cascade des modules et TPs si c'est un professeur
    if user.role == 'professeur':
        from backend.models import Professeur, Module, TP
        professeur = Professeur.query.filter_by(id_professeur=user.id).first()
        if professeur:
            # Supprimer tous les modules de ce prof
            modules = Module.query.filter_by(id_professeur=professeur.id_professeur).all()
            for module in modules:
                # Supprimer tous les TPs de ce module
                tps = TP.query.filter_by(id_module=module.id_module).all()
                for tp in tps:
                    db.session.delete(tp)
                db.session.delete(module)
            db.session.delete(professeur)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "User deleted successfully"}), 200

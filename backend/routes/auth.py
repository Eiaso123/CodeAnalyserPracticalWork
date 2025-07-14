from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.extensions import db, bcrypt
from backend.models import User, Etudiant, Professeur
import datetime
from werkzeug.security import generate_password_hash
import random, time

auth_bp = Blueprint('auth', __name__)

reset_codes = {}

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print('REGISTER DATA:', data)
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'etudiant')
    langue = data.get('langue', 'Français')

    if not (full_name and email and password):
        return jsonify({'message': 'Champs manquants'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Utilisateur déjà existant'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(full_name=full_name, email=email, password=hashed_password, role=role, langue=langue)

    db.session.add(new_user)
    db.session.flush()  
    
    if role == 'etudiant':
        new_etudiant = Etudiant()
        new_etudiant.id_etudiant = new_user.id
        db.session.add(new_etudiant)
    elif role == 'professeur':
        new_prof = Professeur()
        new_prof.id_professeur = new_user.id
        db.session.add(new_prof)

    db.session.commit()  
    token = create_access_token(identity=new_user.id, expires_delta=datetime.timedelta(days=1))

    return jsonify({
        'token': token,
        'user': {
            'id': new_user.id,
            'full_name': new_user.full_name,
            'email': new_user.email,
            'role': new_user.role
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(days=1))
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role
            }
        }), 200

    return jsonify({'message': 'Identifiants invalides'}), 401

#  VERIFY TOKEN
@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Utilisateur introuvable'}), 404
    return jsonify({
        'valid': True,
        'user_id': user.id,
        'role': user.role
    }), 200

@auth_bp.route('/api/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email requis'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': "Utilisateur introuvable"}), 404

    code = str(random.randint(1000, 9999))
    reset_codes[email] = {
        "code": code,
        "expires": int(time.time()) + 300  # 5 min
    }

    # Ici tu dois envoyer le code par SMS/SMS API ! (Demo: print dans la console)
    print(f"Code de réinitialisation pour {email}: {code}")
    # (Optionnel : envoie email aussi si besoin)

    return jsonify({'message': 'Code envoyé'}), 200

@auth_bp.route('/api/verify-reset-code', methods=['POST'])
def verify_reset_code():
    data = request.get_json() or {}
    email = data.get('email')
    code = data.get('code')
    entry = reset_codes.get(email)
    if not entry or entry['code'] != code or time.time() > entry['expires']:
        return jsonify({'error': 'Code incorrect ou expiré'}), 400
    return jsonify({'message': 'Code valide'}), 200

@auth_bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    email = data.get('email')
    code = data.get('code')
    password = data.get('password')

    entry = reset_codes.get(email)
    if not entry or entry['code'] != code or time.time() > entry['expires']:
        return jsonify({'error': 'Code incorrect ou expiré'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': "Utilisateur introuvable"}), 404

    if not password or not isinstance(password, str):
     return jsonify({'error': 'Mot de passe invalide'}), 400
    user.password = generate_password_hash(password)
    db.session.commit()
    reset_codes.pop(email, None)  # Supprimer le code utilisé

    return jsonify({'message': 'Mot de passe modifié'}), 200


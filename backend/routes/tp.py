from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import db
from backend.models import Module, TP, User

tp_bp = Blueprint('tp', __name__)


def _current_user():
    try:
        return db.session.get(User, int(get_jwt_identity()))
    except (TypeError, ValueError):
        return None


@tp_bp.route('/tp', methods=['POST'])
@jwt_required()
def create_tp():
    user = _current_user()
    if not user or user.role != 'professeur':
        return jsonify({'message': 'Accès réservé aux professeurs'}), 403

    data = request.get_json(silent=True) or request.form
    titre = data.get('titre')
    deadline = data.get('deadline')
    id_module = data.get('id_module')
    if not titre or not deadline or not id_module:
        return jsonify({'message': 'titre, deadline et id_module sont requis'}), 400

    try:
        module_id = int(id_module)
        module = db.session.get(Module, module_id)
        if not module or module.id_professeur != user.id:
            return jsonify({'message': 'Module introuvable ou accès refusé'}), 404

        tp = TP(
            titre=titre,
            deadline=deadline,
            statut=data.get('statut', 'Ouvert'),
            path=data.get('path'),
            id_module=module_id,
            max_etudiants=int(data['max_etudiants']) if data.get('max_etudiants') else None,
            download_code=data.get('download_code'),
            id_professeur=user.id,
        )
        db.session.add(tp)
        db.session.commit()
        return jsonify({'message': 'TP créé', 'tp': tp.to_dict()}), 201
    except (TypeError, ValueError) as error:
        db.session.rollback()
        return jsonify({'message': str(error)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création du TP'}), 500


@tp_bp.route('/tp/module/<int:module_id>', methods=['GET'])
@jwt_required()
def get_tps_by_module(module_id):
    tps = TP.query.filter_by(id_module=module_id).order_by(TP.deadline.asc()).all()
    return jsonify({'tps': [tp.to_dict() for tp in tps]}), 200


@tp_bp.route('/tp/<int:tp_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_tp(tp_id):
    tp = db.session.get(TP, tp_id)
    if not tp:
        return jsonify({'message': 'TP introuvable'}), 404

    if request.method == 'GET':
        return jsonify(tp.to_dict()), 200

    user = _current_user()
    if not user or user.role != 'professeur' or tp.id_professeur != user.id:
        return jsonify({'message': 'Accès refusé'}), 403

    if request.method == 'DELETE':
        db.session.delete(tp)
        db.session.commit()
        return jsonify({'message': 'TP supprimé'}), 200

    data = request.get_json(silent=True) or request.form
    try:
        tp.titre = data.get('titre', tp.titre)
        if 'deadline' in data:
            tp.deadline = TP(
                titre=tp.titre,
                deadline=data['deadline'],
                id_module=tp.id_module,
                id_professeur=tp.id_professeur,
            ).deadline
        tp.statut = data.get('statut', tp.statut)
        if tp.statut not in ('Ouvert', 'Fermé'):
            raise ValueError("Statut must be 'Ouvert' or 'Fermé'")
        if 'max_etudiants' in data:
            tp.max_etudiants = int(data['max_etudiants']) if data['max_etudiants'] else None
            if tp.max_etudiants is not None and tp.max_etudiants <= 0:
                raise ValueError('max_etudiants doit être positif')
        tp.path = data.get('path', tp.path)
        tp.download_code = data.get('download_code', tp.download_code)
        db.session.commit()
        return jsonify({'message': 'TP mis à jour', 'tp': tp.to_dict()}), 200
    except (TypeError, ValueError) as error:
        db.session.rollback()
        return jsonify({'message': str(error)}), 400

from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import db
from backend.models import Reponse, TP, User

reponse_bp = Blueprint('reponse', __name__)


def _current_user():
    try:
        return db.session.get(User, int(get_jwt_identity()))
    except (TypeError, ValueError):
        return None


@reponse_bp.route('/reponses', methods=['POST'])
@jwt_required()
def submit_reponse():
    user = _current_user()
    if not user or user.role != 'etudiant':
        return jsonify({'message': 'Accès réservé aux étudiants'}), 403

    data = request.get_json(silent=True) or {}
    content = data.get('reponse') or data.get('contenu')
    tp_id = data.get('id_tp')
    if not content or not tp_id:
        return jsonify({'message': 'id_tp et reponse sont requis'}), 400

    try:
        tp = db.session.get(TP, int(tp_id))
    except (TypeError, ValueError):
        tp = None
    if not tp:
        return jsonify({'message': 'TP introuvable'}), 404
    if tp.statut != 'Ouvert' or (tp.deadline and tp.deadline < date.today()):
        return jsonify({'message': 'La remise de ce TP est fermée'}), 400

    reponse = Reponse(
        reponse=content,
        contenu=data.get('contenu'),
        id_tp=tp.id_tp,
        id_etudiant=user.id,
    )
    db.session.add(reponse)
    db.session.commit()
    return jsonify({
        'message': 'Réponse enregistrée',
        'reponse': {
            'id_reponse': reponse.id_reponse,
            'id_tp': reponse.id_tp,
            'id_etudiant': reponse.id_etudiant,
            'reponse': reponse.reponse,
        },
    }), 201


@reponse_bp.route('/reponses/tp/<int:tp_id>', methods=['GET'])
@jwt_required()
def get_reponses_by_tp(tp_id):
    user = _current_user()
    tp = db.session.get(TP, tp_id)
    if not user or not tp:
        return jsonify({'message': 'TP introuvable'}), 404

    query = Reponse.query.filter_by(id_tp=tp_id)
    if user.role == 'etudiant':
        query = query.filter_by(id_etudiant=user.id)
    elif user.role != 'professeur' or tp.id_professeur != user.id:
        return jsonify({'message': 'Accès refusé'}), 403

    return jsonify({'reponses': [
        {
            'id_reponse': reponse.id_reponse,
            'id_tp': reponse.id_tp,
            'id_etudiant': reponse.id_etudiant,
            'reponse': reponse.reponse,
            'correction': reponse.correction,
            'note': reponse.note,
            'feedback': reponse.feedback,
        }
        for reponse in query.order_by(Reponse.id_reponse.desc()).all()
    ]}), 200
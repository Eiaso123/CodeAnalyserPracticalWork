from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import db
from backend.models import Reponse, User

etudiant_bp = Blueprint('etudiant', __name__)


@etudiant_bp.route('/etudiant/reponses', methods=['GET'])
@jwt_required()
def get_student_reponses():
	try:
		user = db.session.get(User, int(get_jwt_identity()))
	except (TypeError, ValueError):
		user = None
	if not user or user.role != 'etudiant':
		return jsonify({'message': 'Accès réservé aux étudiants'}), 403

	reponses = Reponse.query.filter_by(id_etudiant=user.id).order_by(Reponse.id_reponse.desc()).all()
	return jsonify({'reponses': [
		{
			'id_reponse': reponse.id_reponse,
			'id_tp': reponse.id_tp,
			'reponse': reponse.reponse,
			'correction': reponse.correction,
			'note': reponse.note,
			'feedback': reponse.feedback,
		}
		for reponse in reponses
	]}), 200

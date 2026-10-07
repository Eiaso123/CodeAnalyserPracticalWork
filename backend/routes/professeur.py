from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import db
from backend.models import Module, User

professeur_bp = Blueprint('professeur', __name__)


@professeur_bp.route('/professeur/modules', methods=['GET'])
@jwt_required()
def get_professeur_modules():
	try:
		user = db.session.get(User, int(get_jwt_identity()))
	except (TypeError, ValueError):
		user = None
	if not user or user.role != 'professeur':
		return jsonify({'message': 'Accès réservé aux professeurs'}), 403

	modules = Module.query.filter_by(id_professeur=user.id).order_by(Module.nom.asc()).all()
	return jsonify({'modules': [
		{
			'id_module': module.id_module,
			'nom': module.nom,
			'information': module.information,
			'id_professeur': module.id_professeur,
		}
		for module in modules
	]}), 200

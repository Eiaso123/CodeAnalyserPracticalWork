from flask import Blueprint, request, jsonify
from backend.models import Correction

corrections_bp = Blueprint('corrections', __name__)

@corrections_bp.route('/corrections/by-tp/<int:tp_id>', methods=['GET'])
def get_corrections_by_tp(tp_id):
    corrections = Correction.query.filter_by(id_tp=tp_id).all()
    return jsonify([
        {
            'id_correction': cor.id,  # ← Change here!
            'id_etudiant': cor.id_etudiant,
            'code': cor.code,
            'rapport': cor.rapport,
            'date_submitted': cor.date_submitted
        }
        for cor in corrections
    ])

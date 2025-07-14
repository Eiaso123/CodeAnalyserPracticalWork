from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models import Module, Professeur, TP

module_bp = Blueprint('module_bp', __name__)


@module_bp.route('/api/modules', methods=['GET'])
@jwt_required()
def get_modules():
    modules = Module.query.all()
    modules_list = []
    for m in modules:
        modules_list.append({
            'id_module': m.id_module,
            'nom': m.nom,
            'id_professeur': m.id_professeur,
            'information': m.information
        })
    return jsonify({'modules': modules_list})

@module_bp.route('/api/tp/all', methods=['GET'])
@jwt_required()
def get_all_tps():
    tps = TP.query.all()
    tps_list = []
    for tp in tps:
        tps_list.append({
            'id_tp': tp.id_tp,
            'titre': tp.titre,
            'deadline': tp.deadline.strftime("%Y-%m-%d") if tp.deadline else None,
            'statut': tp.statut,
            'path': tp.path,
            'id_module': tp.id_module,
            'max_etudiants': tp.max_etudiants,
            'download_code': tp.download_code
        })
    return jsonify({'tps': tps_list})
# Create a new module (Professeur only)
@module_bp.route('/module/create', methods=['POST'])
@jwt_required()
def create_module():
    nom = request.form.get('nom')
    information = request.form.get('information')
    id_professeur = request.form.get('id_professeur')

    # Champs obligatoires
    if not (nom and id_professeur):
        return jsonify({'msg': 'Champs manquants'}), 400

    try:
        id_professeur = int(id_professeur)
        module = Module(nom=nom, information=information, id_professeur=id_professeur)
        db.session.add(module)
        db.session.commit()
        return jsonify({
            'msg': 'Module créé',
            'module': {
                'id_module': module.id_module,
                'nom': module.nom,
                'information': module.information,
                'id_professeur': module.id_professeur
            }
        }), 201
    except Exception as e:
        print("Erreur backend module:", e) 
        return jsonify({'msg': f'Erreur: {str(e)}'}), 500

# Update a module
@module_bp.route('/module/<int:id_module>', methods=['PUT'])
@jwt_required()
def update_module(id_module):
    module = Module.query.get(id_module)
    if not module:
        return jsonify({'msg': 'Module non trouvé'}), 404

    data = request.form
    module.nom = data.get('nom', module.nom)
    module.information = data.get('information', module.information)
    module.id_professeur = data.get('id_professeur', module.id_professeur)

    db.session.commit()
    return jsonify({
        'msg': 'Module mis à jour',
        'module': {
            'id_module': module.id_module,
            'nom': module.nom,
            'information': module.information,
            'id_professeur': module.id_professeur
        }
    }), 200

# Delete a module
@module_bp.route('/module/<int:id_module>', methods=['DELETE'])
@jwt_required()
def delete_module(id_module):
    module = Module.query.get(id_module)
    if not module:
        return jsonify({'msg': 'Module non trouvé'}), 404
    db.session.delete(module)
    db.session.commit()
    return jsonify({'msg': 'Module supprimé'}), 200

# List all modules
@module_bp.route('/modules', methods=['GET'])
@jwt_required()
def list_modules():
    modules = Module.query.all()
    return jsonify(
        modules=[{
            'id_module': m.id_module,
            'nom': m.nom,
            'information': m.information,
            'id_professeur': m.id_professeur
        } for m in modules]
    ), 200


# Get a single module by ID
@module_bp.route('/module/<int:id_module>', methods=['GET'])
@jwt_required()
def get_module(id_module):
    module = Module.query.get(id_module)
    if not module:
        return jsonify({'msg': 'Module non trouvé'}), 404
    return jsonify({
        'id_module': module.id_module,
        'nom': module.nom,
        'information': module.information,
        'id_professeur': module.id_professeur
    }), 200

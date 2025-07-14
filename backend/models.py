from backend.extensions import db
from datetime import datetime



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    langue = db.Column(db.String(50), nullable=True)

    etudiant = db.relationship('Etudiant', backref='user', uselist=False, cascade="all, delete")
    professeur = db.relationship('Professeur', backref='user', uselist=False, cascade="all, delete")

    def __init__(self, full_name, email, password, role, langue=None):
        self.full_name = full_name
        self.email = email
        self.password = password
        self.role = role
        self.langue = langue
    

    def __repr__(self):
        return f"<User {self.full_name}>"

    _mapper_args_ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }

class Etudiant(db.Model):
    __tablename__ = 'etudiant'

    id_etudiant = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    _mapper_args_ = {
        'polymorphic_identity': 'etudiant'
    }

    def __repr__(self):
        return f"<Etudiant {self.id_etudiant}>"

class Professeur(db.Model):
    __tablename__ = 'professeur'

    id_professeur = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    _mapper_args_ = {
        'polymorphic_identity': 'professeur'
    }

    def __repr__(self):
        return f"<Professeur {self.id_professeur}>"
class Module(db.Model):
    __tablename__ = 'module'

    id_module = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    id_professeur = db.Column(db.Integer, db.ForeignKey('professeur.id_professeur'), nullable=False)
    information = db.Column(db.Text, nullable=True)

    tps = db.relationship('TP', backref='module', cascade="all, delete-orphan", lazy=True)
    inscriptions = db.relationship('Inscription', backref='module', cascade="all, delete")

    def __init__(self, nom, information=None, id_professeur=None):
        self.nom = nom
        self.information = information
        self.id_professeur = id_professeur  

    def __repr__(self):
        return f"<Module {self.nom}>"

class Inscription(db.Model):
    __tablename__ = 'inscription'

    id_etudiant = db.Column(db.Integer, db.ForeignKey('etudiant.id_etudiant'), primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    id_module = db.Column(db.Integer, db.ForeignKey('module.id_module'), primary_key=True)
    file_url = db.Column(db.String(200))
    download_code = db.Column(db.String(50), nullable=False)
    max_etudiants = db.Column(db.Integer, default=50)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Inscription Etudiant:{self.id_etudiant} Module:{self.id_module}>"

class TP(db.Model):
    __tablename__ = 'tp'

    id_tp = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(20), nullable=False)  # 'Ouvert' ou 'Fermé'
    path = db.Column(db.String(255), nullable=True)
    id_module = db.Column(db.Integer, db.ForeignKey('module.id_module'), nullable=False)
    max_etudiants = db.Column(db.Integer, nullable=True)
    download_code = db.Column(db.String(50), nullable=True)
    id_professeur = db.Column(db.Integer, db.ForeignKey('professeur.id_professeur'), nullable=False)

    reponses = db.relationship('Reponse', backref='tp', cascade="all, delete")

    def __init__(self, titre, deadline, statut='Ouvert', path=None, id_module=None, max_etudiants=None, download_code=None, id_professeur=None):
        if isinstance(deadline, str):
            try:
                deadline = datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid deadline format. Use YYYY-MM-DD")
        if not isinstance(deadline, datetime):
            raise TypeError("Deadline must be a datetime object or string in YYYY-MM-DD format")

        if not isinstance(titre, str) or not titre.strip():
            raise ValueError("Titre must be a non-empty string")

        if statut not in ['Ouvert', 'Fermé']:
            raise ValueError("Statut must be 'Ouvert' or 'Fermé'")

        if id_module is None or not isinstance(id_module, int) or id_module <= 0:
            raise ValueError("id_module must be a positive integer")

        if path is not None and (not isinstance(path, str) or not path.strip()):
            raise ValueError("Path must be a non-empty string if provided")

        if max_etudiants is not None and (not isinstance(max_etudiants, int) or max_etudiants <= 0):
            raise ValueError("Max_etudiants must be a positive integer")

        if download_code is not None and (not isinstance(download_code, str) or not download_code.strip()):
            raise ValueError("Download_code must be a non-empty string if provided")

        self.titre = titre
        self.deadline = deadline
        self.statut = statut
        self.path = path
        self.id_module = id_module
        self.max_etudiants = max_etudiants
        self.download_code = download_code
        self.id_professeur = id_professeur 
        if self.statut not in ['Ouvert', 'Fermé']:
            raise ValueError("Statut must be 'Ouvert' or 'Fermé'")

    def __repr__(self):
        return f"<TP {self.titre}>"
    def to_dict(self):
        return {
            "id_tp": self.id_tp,
            "titre": self.titre,
            "deadline": self.deadline.strftime('%Y-%m-%d') if self.deadline else None,
            "statut": self.statut,
            "path": self.path,
            "id_module": self.id_module,
            "max_etudiants": self.max_etudiants,
            "download_code": self.download_code,
            "id_professeur": self.id_professeur,
        }


class Reponse(db.Model):
    __tablename__ = 'reponse'

    id_reponse = db.Column(db.Integer, primary_key=True)
    reponse = db.Column(db.Text, nullable=False)
    correction = db.Column(db.Text, nullable=True)
    note = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    contenu = db.Column(db.Text, nullable=True)

    id_tp = db.Column(db.Integer, db.ForeignKey('tp.id_tp'), nullable=False)
    id_etudiant = db.Column(db.Integer, db.ForeignKey('etudiant.id_etudiant'), nullable=False)

    def __repr__(self):
        return f"<Reponse TP:{self.id_tp} Etudiant:{self.id_etudiant}>"
    
class Correction(db.Model):
    __tablename__ = 'corrections'
    id = db.Column(db.Integer, primary_key=True)
    id_etudiant = db.Column(db.Integer, nullable=False)
    id_tp = db.Column(db.Integer, nullable=False)
    code = db.Column(db.Text, nullable=False)
    rapport = db.Column(db.Text, nullable=False)
    pdf_path = db.Column(db.String(255)) 
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    def __init__(self, id_etudiant, id_tp, code, rapport, pdf_path=None):
        self.id_etudiant = id_etudiant
        self.id_tp = id_tp
        self.code = code
        self.rapport = rapport
        self.pdf_path = pdf_path
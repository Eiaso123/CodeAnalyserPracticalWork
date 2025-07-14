from backend.extensions import db
from sqlalchemy import text
from backend.app import app  # Importer l'app ici seulement


def create_professeur_view():
    view_sql = """
    CREATE VIEW IF NOT EXISTS professeur_view AS
    SELECT p.id_professeur, u.full_name, u.email, u.password
    FROM professeur p
    JOIN user u ON p.id_professeur = u.id;
    """
    with app.app_context():
        with db.engine.connect() as connection:
            connection.execute(text(view_sql))
        print("Vue professeur_view créée avec succès.")

if __name__ == '__main__':
    create_professeur_view()

import sqlite3
import csv
from io import StringIO
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """
    Classe pour gérer les interactions avec la base de données SQLite.
    """
    def __init__(self, db_path='db/database.db'):
        """
        Initialise la classe avec le chemin de la base de données.

        :param db_path: Chemin vers le fichier de la base de données SQLite
        """
        self.db_path = db_path
        self.connection = None

    def get_connection(self):
        """
        Retourne une connexion à la base de données.
        Crée une nouvelle connexion si nécessaire.

        :return: Objet de connexion SQLite
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def close_connection(self):
        """
        Ferme la connexion à la base de données si elle existe.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def insert_data_to_db(self, csv_content):
        """
        Insère les données du CSV dans la table violations de la base SQLite.

        :param csv_content: Contenu texte du fichier CSV
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            csv_file = StringIO(csv_content)
            reader = csv.DictReader(csv_file)

            insert_query = """
                INSERT INTO violations (
                    id_poursuite, business_id, date, description, adresse,
                    date_jugement, etablissement, montant, proprietaire,
                    ville, statut, date_statut, categorie
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for row in reader:
                cursor.execute(insert_query, (
                    row['id_poursuite'],
                    row['business_id'],
                    row['date'],
                    row['description'],
                    row['adresse'],
                    row['date_jugement'],
                    row['etablissement'],
                    row['montant'],
                    row['proprietaire'],
                    row['ville'],
                    row['statut'],
                    row['date_statut'],
                    row['categorie']
                ))

            conn.commit()
            logger.info("Données insérées dans la base avec succès.")
        except sqlite3.Error as e:
            logger.error(f"Erreur SQLite lors de l'insertion : {e}")
            raise
        except KeyError as e:
            logger.error(f"Colonne manquante dans le CSV : {e}")
            raise

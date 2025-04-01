import sqlite3
import csv
from io import StringIO


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


    def insert_data_to_db(self, csv_content):
        """
        Insère les données du CSV dans la table violations de la base SQLite.

        :param csv_content: Contenu texte du fichier CSV
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM violations")
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
            print("Données insérées dans la base avec succès.")
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de l'insertion : {e}")
            raise
        except KeyError as e:
            print(f"Colonne manquante dans le CSV : {e}")
            raise


    def search_violation(self, search_type, query):
        if len(query) < 3:
            return []
        """
            Recherche les violations selon le type et la requête.

            :param search_type: Type de recherche (etablissement, proprietaire, rue)
            :param query: Chaîne de recherche
            :return: Liste de violations correspondant à la recherche
        """
        cursor = self.get_connection().cursor()
        if search_type == "etablissement":
            sql = "SELECT * FROM violations WHERE etablissement LIKE ?"
        elif search_type == "proprietaire":
            sql = "SELECT * FROM violations WHERE proprietaire LIKE ?"
        elif search_type == "rue":
            sql = "SELECT * FROM violations WHERE adresse LIKE ?"
        else: 
            return [] 
        cursor.execute(sql, (f"%{query}%",))
        results = cursor.fetchall()
        # Récupére les noms des colonnes
        columns = [desc[0] for desc in cursor.description]
        # Convertit chaque tuple en dictionnaire
        return [dict(zip(columns, row)) for row in results]


    def get_violations_by_date(self, start_date, end_date):
        """
        Récupère les violations entre deux dates.

        :param start_date: Date de début au format ISO 8601 (YYYY-MM-DD)
        :param end_date: Date de fin au format ISO 8601 (YYYY-MM-DD)
        :return: Liste de violations
        """
        cursor = self.get_connection().cursor()
        query = "SELECT * FROM violations WHERE date BETWEEN ? AND ?"
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]
  

    def get_establishment_names(self):
        """
        Récupère une liste triée des noms d'établissements (distinct).
        :return: Liste de noms d'établissements (strings).
        """
        cursor = self.get_connection().cursor()
        query = "SELECT DISTINCT etablissement FROM violations WHERE " \
        "etablissement IS NOT NULL AND etablissement != '' ORDER BY etablissement"
        cursor.execute(query)
        results = [row[0] for row in cursor.fetchall()]
        return results


    def get_infractions_by_establishment(self, establishment_name, start_date, end_date):
        """
        Récupère toutes les infractions d'un nom d'établissement donné à une période donnée.
        :param establishment_name: Nom de l'établissement.
        :param start_date: Date de début au format ISO 8601 (YYYY-MM-DD)
        :param end_date: Date de fin au format ISO 8601 (YYYY-MM-DD)
        :return: Liste de dictionnaires, chacun représentant une infraction.
        """
        cursor = self.get_connection().cursor()
        query = "SELECT * FROM violations WHERE etablissement = ?" \
        "AND date BETWEEN ? AND ? ORDER BY date DESC"
        cursor.execute(query, (establishment_name, start_date, end_date))
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]
  
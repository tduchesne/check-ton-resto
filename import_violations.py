from database import Database
import logging
import requests


# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL du fichier CSV
CSV_URL = "https://data.montreal.ca/dataset/" \
          "05a9e718-6810-4e73-8bb9-5955efeb91a0/" \
          "resource/7f939a08-be8a-45e1-b208-d8744dc" \
          "a8fc6/download/violations.csv"


def download_csv(url):
    """Télécharge le fichier CSV depuis l'URL et retourne son contenu."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info("Données téléchargées avec succès.")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Erreur lors du téléchargement : {e}")
        raise


def main():
    db = Database()
    try:
        logger.info("Début de l'importation...")
        csv_content = download_csv(CSV_URL)
        db.insert_data_to_db(csv_content)
        logger.info("Importation terminée !")
    except Exception as e:
        logger.error(f"Échec de l'importation : {e}")
    finally:
        db.close_connection()


if __name__ == "__main__":
    main()

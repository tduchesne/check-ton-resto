from database import Database
import requests
import yaml
import smtplib
from email.message import EmailMessage
import os
from io import StringIO
import csv
import sqlite3
import tweepy

# URL du fichier CSV
CSV_URL = "https://data.montreal.ca/dataset/" \
          "05a9e718-6810-4e73-8bb9-5955efeb91a0/" \
          "resource/7f939a08-be8a-45e1-b208-d8744dc" \
          "a8fc6/download/violations.csv"
CONFIG_FILE = "config.yaml"
KNOWN_IDS_FILEPATH = "db/known_ids.txt"


def download_csv(url):
    """Télécharge le fichier CSV depuis l'URL et retourne son contenu."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        print("Données téléchargées avec succès.")
        return response.text
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement : {e}")
        raise


def parse_csv_content(csv_content):
    """Parse le contenu CSV et retourne une liste
    de dictionnaires et un set d'IDs."""
    csv_file = StringIO(csv_content)
    reader = csv.DictReader(csv_file)
    violations_list = []
    ids_set = set()
    try:
        for row in reader:
            violations_list.append(row)
            ids_set.add(row['id_poursuite'])
    except KeyError as e:
        print(f"ERREUR: Colonne manquante dans le CSV lors du parsing : {e}")
        raise
    return violations_list, ids_set


def update_db():
    """Télécharge, compare, notifie et met à jour la base de données."""
    db = Database()
    config = load_config()

    try:
        print("Début de la mise à jour...")
        csv_content = download_csv(CSV_URL)

        # Parser les données actuelles
        current_violations_list, current_ids_set = parse_csv_content(
                                                    csv_content)
        print(f"""{len(current_ids_set)}
              IDs uniques trouvés dans les données téléchargées.""")

        # Charger les anciens IDs connus
        old_ids_set = load_known_ids()
        print(f"{len(old_ids_set)} IDs étaient connus précédemment.")

        # Trouver les nouveaux IDs
        new_ids_set = current_ids_set - old_ids_set
        print(f"{len(new_ids_set)} nouveaux IDs détectés.")

        # Si de nouveaux IDs sont trouvés, préparer et envoyer l'email
        if new_ids_set:
            print("Préparation de la notification "
                  "pour les nouvelles contraventions...")
            # Filtrer la liste complète pour obtenir
            # les détails des nouvelles violations
            new_violations_details = [
                violation for violation in current_violations_list
                if violation['id_poursuite'] in new_ids_set
            ]
            # Envoyer l'email
            if config:
                print("Tentative d'envoi de l'email...")
                send_notification_email(new_violations_details, config)
            else:
                print("Notification non envoyée car "
                      "la configuration n'a pas pu être chargée.")
            # Publier sur Twitter
            if config:
                print("Tentative de publication sur Twitter...")
                post_new_violations_to_twitter(new_violations_details, config)
            else:
                print("Tweet non envoyé car "
                      "la configuration n'a pas pu être chargée.")

        # Insérer les données actuelles dans la BDD
        print("Insertion des données actuelles dans la base de données...")
        db.insert_data_to_db(csv_content)
        print("Insertion terminée.")

        # Si l'insertion a réussi, sauvegarder l'état actuel des IDs
        print("Sauvegarde des IDs actuels...")
        save_known_ids(current_ids_set)

        print("Mise à jour terminée avec succès !")

    except requests.RequestException as e:
        print(f"Échec de la mise à jour : Erreur de téléchargement - {e}")
    except sqlite3.Error as e:
        print(f"Échec de la mise à jour : Erreur de base de données - {e}")
    except Exception as e:
        print(f"Échec de la mise à jour : Erreur inattendue - {e}")
    finally:
        db.close_connection()


def load_known_ids(filepath=KNOWN_IDS_FILEPATH):
    """Charge les IDs connus depuis un fichier texte dans un set."""
    known_ids = set()
    try:
        with open(filepath, 'r') as f:
            for line in f:
                cleaned_line = line.strip()
                if cleaned_line:
                    known_ids.add(cleaned_line)
    except FileNotFoundError:
        print(f"""Fichier des IDs connus '{filepath}' non trouvé.
              Création d'un nouveau fichier.""")
    return known_ids


def save_known_ids(ids_set, filepath=KNOWN_IDS_FILEPATH):
    """Sauvegarde un set d'IDs dans un fichier texte, un ID par ligne."""
    try:
        # S'assure que le répertoire existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            list_ids = sorted(list(ids_set))
            for violation_id in list_ids:
                f.write(f"{violation_id}\n")
        print(f"IDs connus sauvegardés dans '{filepath}'.")
    except IOError as e:
        print(f"""Erreur lors de la sauvegarde des IDs
              connus dans '{filepath}': {e}""")


def load_config(filepath=CONFIG_FILE):
    """Charge la configuration depuis un fichier YAML."""
    try:
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
            if not config or not all(key in config for key in
                                     ['email_recipient', 'smtp_settings']):
                raise ValueError("""Configuration YAML invalide ou manquante
                                  (email_recipient/smtp_settings requis).""")
            return config
    except FileNotFoundError:
        print(f"ERREUR: Fichier de configuration '{filepath}' non trouvé.")
        return None
    except yaml.YAMLError as e:
        print(f"""ERREUR: Impossible de parser le
              fichier YAML '{filepath}': {e}""")
        return None
    except ValueError as e:
        print(f"ERREUR: {e}")
        return None


def send_notification_email(new_violations_details, config):
    """Envoie un email de notification avec
     les détails des nouvelles violations."""
    if not config:
        print("Configuration non chargée, impossible d'envoyer l'email.")
        return

    recipient = config.get('email_recipient')
    smtp_config = config.get('smtp_settings')

    if not recipient or not smtp_config:
        print("""Configuration email incomplète
              (destinataire ou paramètres SMTP).""")
        return

    subject = "Nouvelles contraventions détectées"
    body_intro = f"""Bonjour,\n\n{len(new_violations_details)}
     nouvelle(s) contravention(s) ont été détectée(s)
     depuis la dernière mise à jour :\n\n"""
    body_details = ""
    for violation in new_violations_details:
        body_details += (
            f"- Établissement: {violation.get('etablissement', 'N/A')}\n"
            f"  Date: {violation.get('date', 'N/A')}\n"
            f"  Description: {violation.get('description', 'N/A')}\n"
            f"  Adresse: {violation.get('adresse', 'N/A')}\n\n"
        )

    msg = EmailMessage()
    msg.set_content(body_intro + body_details)
    msg['Subject'] = subject
    msg['From'] = smtp_config.get('username')
    msg['To'] = recipient

    try:
        server = None
        host = smtp_config.get('host')
        port = smtp_config.get('port')
        use_tls = smtp_config.get('use_tls', False)
        username = smtp_config.get('username')
        password = smtp_config.get('password')

        print(f"Tentative de connexion à {host}:{port}...")
        server = smtplib.SMTP(host, port)
        if use_tls:
            server.starttls()

        if username and password:
            print("Authentification SMTP...")
            server.login(username, password)
        else:
            print("Connexion SMTP sans authentification.")

        print(f"Envoi de l'email à {recipient}...")
        server.send_message(msg)
        print("Email envoyé avec succès.")

    except smtplib.SMTPAuthenticationError:
        print("""ERREUR SMTP: Échec de l'authentification.
              Vérifiez username/password/mot de passe d'application.""")
    except smtplib.SMTPException as e:
        print(f"ERREUR SMTP: Impossible d'envoyer l'email : {e}")
    except Exception as e:
        print(f"ERREUR inattendue lors de l'envoi de l'email: {e}")
    finally:
        if server:
            server.quit()
            print("Connexion SMTP fermée.")


def post_new_violations_to_twitter(new_violations_details, config):
    """Publie le nom des établissements ayant de nouvelles
    contraventions sur Twitter."""
    if not config or "twitter_api_credentials" not in config:
        print("Configuration Twitter non chargée, impossible de tweeter.")
        return
    credentials = config.get("twitter_api_credentials")
    required_keys = ["api_key",
                     "api_secret",
                     "access_token",
                     "access_token_secret"]
    if not credentials or not all(key in credentials for key in required_keys):
        print("Configuration Twitter incomplète dans config.yaml.")
        return
    if not new_violations_details:
        print("Aucune nouvelle contravention à tweeter.")
        return
    # Extraire les noms des établissements
    establishment_names = set()
    for violation in new_violations_details:
        name = violation.get("etablissement")
        if name:
            establishment_names.add(name.strip())
    if not establishment_names:
        print("""Aucun nom d'établissement trouvé
              dans les nouvelles violations.""")
        return
    # Construire le message Twitter
    prefix_message = f"Nouvelle(s) contravention(s) détectées(s) pour : "
    names_string = ""
    char_limit = 250  # Limite de caractères pour Twitter moins une marge
    names_list = sorted(list(establishment_names))
    first_name = True
    for name in names_list:
        separator = "" if first_name else ", "
        if len(names_string) + len(separator) + len(name) <= char_limit:
            names_string += separator + name
            first_name = False
        else:
            names_string += separator + "..."
            break
    tweet_text = prefix_message + names_string
    # Authentification et publication via Tweepy
    try:
        client = tweepy.Client(
            consumer_key=credentials["api_key"],
            consumer_secret=credentials["api_secret"],
            access_token=credentials["access_token"],
            access_token_secret=credentials["access_token_secret"]
        )
        response = client.create_tweet(text=tweet_text)
        print(f"Tweet publié avec succès : {response.data['text']}")
        print(f"""Lien du Tweet :
              https://twitter.com/MrTest4269/status/{response.data['id']}""")
    except tweepy.TweepyException as e:
        print(f"Erreur lors de la publication du Tweet : {e}")
    except Exception as e:
        print(f"Erreur inattendue lors de la publication du Tweet : {e}")


if __name__ == "__main__":
    update_db()

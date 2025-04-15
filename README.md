# Check Ton Resto

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/flask-3.0%2B-orange.svg)](https://flask.palletsprojects.com/)


Application web Flask pour visualiser et interagir avec les données ouvertes des contraventions d'inspections alimentaires de la Ville de Montréal.

**[http://checktonresto.pythonanywhere.com](http://checktonresto.pythonanywhere.com)**

## Description

Ce projet récupère les données publiques des constats d'infraction liés aux inspections alimentaires à Montréal. Il offre une interface web permettant de rechercher et visualiser ces contraventions, une API REST pour accéder aux données par programmation, et des notifications automatiques pour les nouvelles infractions détectées.

## Fonctionnalités Principales

*   **Interface de Recherche :**
    *   Recherche par date avec résultats interactifs (AJAX).
    *   Recherche générale par nom d'établissement, propriétaire ou rue.
    *   Vue détaillée des infractions pour un établissement sélectionné.
*   **Synchronisation Automatique :** Mise à jour quotidienne des données depuis la source officielle.
*   **Notifications :**
    *   Envoi d'un email récapitulatif des nouvelles contraventions détectées.
    *   Publication automatique sur Twitter des noms d'établissements concernés par de nouvelles infractions.
*   **API REST :**
    *   Endpoint pour récupérer les contraventions par intervalle de dates (JSON).
    *   Endpoints pour lister les établissements triés par nombre d'infractions (JSON et XML).
    *   Documentation de l'API disponible via l'endpoint `/doc`.
*   **Déploiement :** Application déployée et accessible en ligne.

## Technologies Utilisées

*   **Backend :** Python 3, Flask 3
*   **Base de Données :** SQLite 3
*   **Frontend :** HTML5, CSS3, JavaScript (Vanilla JS avec Fetch API)
*   **Styling :** Bootstrap 5.3
*   **Tâches Planifiées :** APScheduler (localement), Scheduled Task (PythonAnywhere)
*   **Notifications :** smtplib (Email), Tweepy (Twitter API v2)
*   **Configuration :** PyYAML, python-dotenv (pour les variables d'environnement)
*   **API Documentation :** RAML 1.0, raml2html

## Installation et Lancement Local

1.  **Prérequis :** Python 3.9+, `pip`, Git. (Environnement virtuel recommandé).
2.  **Cloner :** `git clone <url_du_depot> && cd <nom_du_repertoire>`
3.  **Installer :** `pip install -r requirements.txt`
4.  **Configurer :**
    *   Créez un fichier `.env` à la racine (voir `.gitignore`).
    *   Remplissez `.env` avec les secrets requis (voir section Configuration ci-dessous).
    *   Vérifiez/Adaptez `config.yaml` pour les paramètres non sensibles.
5.  **Initialiser DB :** `sqlite3 db/database.db < db/db.sql`
6.  **Import Initial :** `python data_sync.py` (ou nom du script)
7.  **Lancer :** `flask run` (ou `make run`)
    *   Accès via `http://127.0.0.1:5000`.

## Configuration

L'application utilise `config.yaml` pour les paramètres non sensibles et des **variables d'environnement** pour les secrets. En développement local, ces variables peuvent être chargées depuis un fichier `.env` (ignoré par Git).

**Variables d'Environnement Requises :**

*   `SMTP_USERNAME`: Identifiant du compte email pour l'envoi.
*   `SMTP_PASSWORD`: Mot de passe (ou mot de passe d'application) du compte email.
*   `TWITTER_API_KEY`: Clé API Twitter.
*   `TWITTER_API_SECRET`: Secret API Twitter.
*   `TWITTER_ACCESS_TOKEN`: Jeton d'accès Twitter.
*   `TWITTER_ACCESS_TOKEN_SECRET`: Secret du jeton d'accès Twitter.

**Variables Optionnelles / Configurables via `.env` ou `config.yaml` :**

*   `EMAIL_RECIPIENT`: Destinataire des emails de notification (B1).
*   `SMTP_HOST`, `SMTP_PORT`, `SMTP_USE_TLS`: Paramètres du serveur SMTP (B1).
*   `FLASK_DEBUG`: Mettre à `1` pour activer le mode debug de Flask localement.

## Documentation API

La documentation de l'API REST (format RAML) est disponible via l'endpoint `/doc` de l'application web.

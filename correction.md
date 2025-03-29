# INF5190 - Projet de session : Notes pour la correction

Ce document détaille comment tester les différentes fonctionnalités implémentées.

## A1 - Importation initiale des données

Cette étape peuple la base de données SQLite (`db/database.db`) à partir du fichier source distant.

Pour importer les données initiales dans la base de données :
1. **Création de la structure de la base de données :**

Assurez-vous que le répertoire db/ existe. Exécutez la commande suivante à la racine du projet pour créer les tables nécessaires en utilisant le script db/db.sql :
   ```bash
   sqlite3 db/database.db < db/db.sql
   ```

2. **Importation des données depuis le CSV :**

Exécutez le script Python suivant pour télécharger le fichier CSV des violations et l'insérer dans la base de données SQLite créée à l'étape précédente :

    python import_violations.py

*(Note : Ce script efface les données existantes avant l'importation pour garantir un état frais).*    

## A2 - Outil de recherche (Page d'accueil)
Cette fonctionnalité permet de rechercher des contraventions via un formulaire.

1. **Lancement de l'application :**

Utilisez la commande suivante à la racine du projet:
```bash
make
## Ou flask run
```
2. **Test de recherche :**

Accédez à l'application via un navigateur http://127.0.0.1:5000/  et utilisez le premier formulaire de recherche.

 ## A3 - Synchronisation quotidienne

Cette fonctionnalité met automatiquement à jour la base de données chaque jour à minuit.

- **Fonctionnement :** Le scheduler est initialisé au démarrage de l'application Flask (`app.py`). La tâche `update_db` (qui exécute la même logique que `import_violations.py`) est programmée pour s'exécuter quotidiennement. Des messages sont affichés dans la console Flask lors de l'ajout de la tâche et lors de son exécution.

- **Note importante** : En mode debug (`FLASK_DEBUG=1`), le reloader de Flask recharge `app.py`, ce qui entraîne une double initialisation du scheduler et des exécutions simultanées. Mettre `FLASK_DEBUG=0` dans le makefile pour tester sans logs en doublon.

## A4 - API RESTful pour les contrevenants par date

Cette fonctionnalité propose une API pour récupérer les contraventions dans un intervalle de dates spécifié.

- **Endpoint `GET /contrevenants` :**
  - **Paramètres :** `du` (date de début), `au` (date de fin). Les dates doivent être au format ISO 8601 (`YYYY-MM-DD`).
  - **Réponse :** Retourne un tableau JSON contenant les détails complets des contraventions émises entre les dates `du` et `au` inclusivement.
  - **Codes de retour :** `200 OK` en cas de succès, `400 Bad Request` si les paramètres `du`/`au` sont manquants ou si les dates ne sont pas au format ISO 8601.
  - **Exemple de test en ligne de commande :**
  ```bash
  # Requête valide
  curl "http://127.0.0.1:5000/contrevenants?du=2023-01-01&au=2023-01-31"

  # Requête invalide (paramètre manquant)
  curl "http://127.0.0.1:5000/contrevenants?du=2023-01-01"
  ```
- **Endpoint `GET /doc` :**
  - **Fonctionnement :** Sert le fichier statique `static/docs/doc.html`, qui contient la documentation de l'API (format RAML rendu en HTML).
  - **Réponse :** Retourne le contenu HTML du fichier avec un statut `200 OK`. Si le fichier n'est pas trouvé, retourne `404 Not Found`.
  - **Exemple de test (ligne de commande ou navigateur) :**
  ```bash
  curl http://127.0.0.1:5000/doc
  # Ou ouvrir http://127.0.0.1:5000/doc dans un navigateur.
  ```

## A5 - Recherche rapide par date (AJAX)
Cette fonctionnalité ajoute une recherche par date sur la page d'accueil qui utilise l'API A4 via AJAX pour afficher les résultats sans rechargement de page. 

1. **Accès :** Allez sur la page d'accueil http://127.0.0.1:5000/. Trouvez le formulaire intitulé "Recherche Rapide par Date" (sous le formulaire de recherche A2).
2. **Test avec des dates valides** (ex: 2023-01-01 à 2023-01-31) :

    - **Attendu :** Un tableau (colonnes: Établissement, Nombre de contraventions) s'affiche sous le formulaire sans rechargement de page, résumant les contraventions par établissement pour la période.
3. **Test avec une période sans résultats** (ex: 2020-01-01 à 2020-01-02) :
    - **Attendu :** Le message "Aucune contravention trouvée..." s'affiche sans rechargement de page.
4. **Test avec des dates invalides** (date manquante, début > fin) :
    - **Attendu :** Un message d'erreur de validation apparaît près des champs de date sans rechargement de page. Aucun appel API n'est effectué. La zone de résultats reste vide/effacée.

# INF5190 - Projet de session : Notes pour la correction

Ce document détaille comment tester les différentes fonctionnalités implémentées.

## Configuration Générale (Email et Twitter)
Ce projet utilise des variables d'environnement pour gérer les informations sensibles (identifiants SMTP, clés API Twitter) afin de ne pas les stocker directement dans le code source ou dans `config.yaml`.

**Pour le développement local :**

1. Créez un fichier `.env` à la racine du projet.
2. Remplir le fichier .env avec les informations suivantes (voir section **B2** pour savoir comment avoir les secrets Twitter):
```bash
# .env - Fichier pour variables d'environnement locales

# secrets SMTP
SMTP_USERNAME="remplir ici"
SMTP_PASSWORD="remplir ici" 

# secrets Twitter
TWITTER_API_KEY="remplir ici"
TWITTER_API_SECRET="remplir ici"
TWITTER_ACCESS_TOKEN="remplir ici"
TWITTER_ACCESS_TOKEN_SECRET="remplir ici"
```

3. **Fichier config.yaml :** Ce fichier contient des configurations non sensibles (comme `email_recipient`, `smtp_settings.host`, etc.).

**Pour le déploiement (PythonAnywhere) :**
Les mêmes variables d'environnement (`EMAIL_RECIPIENT`, `SMTP_HOST`, `SMTP_PASSWORD`, `TWITTER_API_KEY`, etc.) seront configurées directement dans les paramètres d'environnement de la plateforme d'hébergement.

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

    python data_sync

*(Note : Ce script efface les données existantes avant l'importation pour garantir un état frais).*    

---

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

---

 ## A3 - Synchronisation quotidienne

Cette fonctionnalité met automatiquement à jour la base de données chaque jour à minuit.

- **Fonctionnement :** Le scheduler est initialisé au démarrage de l'application Flask (`app.py`). La tâche `update_db` (qui exécute la même logique que `data_sync`) est programmée pour s'exécuter quotidiennement. Des messages sont affichés dans la console Flask lors de l'ajout de la tâche et lors de son exécution.

- **Note importante** : En mode debug (`FLASK_DEBUG=1`), le reloader de Flask recharge `app.py`, ce qui entraîne une double initialisation du scheduler et des exécutions simultanées. Mettre `FLASK_DEBUG=0` dans le makefile pour tester sans logs en doublon.

---

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

---

## A5 - Recherche rapide par date (AJAX)
Cette fonctionnalité ajoute une recherche par date sur la page d'accueil qui utilise l'API A4 via AJAX pour afficher les résultats sans rechargement de page. 

1. **Accès :** Allez sur la page d'accueil http://127.0.0.1:5000/. Trouvez le formulaire intitulé "Recherche Rapide par Date" (sous le formulaire de recherche A2).
2. **Test avec des dates valides** (ex: 2023-01-01 à 2023-01-31) :

    - **Attendu :** Un tableau (colonnes: Établissement, Nombre de contraventions) s'affiche sous le formulaire sans rechargement de page, résumant les contraventions par établissement pour la période.
3. **Test avec une période sans résultats** (ex: 2020-01-01 à 2020-01-02) :
    - **Attendu :** Le message "Aucune contravention trouvée..." s'affiche sans rechargement de page.
4. **Test avec des dates invalides** (date manquante, début > fin) :
    - **Attendu :** Un message d'erreur de validation apparaît près des champs de date sans rechargement de page. Aucun appel API n'est effectué. La zone de résultats reste vide/effacée.

---

## A6 - Vue détaillée des infractions (AJAX)

Cette fonctionnalité permet de visualiser les détails spécifiques des infractions pour un établissement sélectionné depuis le résumé de la recherche par date.

1.  **Test du Fonctionnement :**
    *   **Afficher le Résumé A5 :**
        *   Effectuez d'abord une recherche par date via le formulaire A5 qui retourne au moins un établissement avec des contraventions.
        *   Le tableau résumé A5 (Établissement, Nombre) s'affiche.
    *   **Afficher les Détails :**
        *   **Cliquez sur le nom** d'un établissement dans la colonne "Établissement" du tableau résumé.
        *   **Attendu :**
            *   Le tableau résumé est remplacé sans rechargement de page.
            *   Un nouveau tableau apparaît, affichant les détails complets (ID, Date, Description, Adresse, etc.) de chaque infraction commise par cet établissement durant la période de dates initialement recherchée.
          
---

## B1 - Notification par email des nouvelles contraventions

Cette fonctionnalité détecte les contraventions ajoutées et envoie un email via SMTP.

1.  **Configuration Préalable :**

- Assurez-vous que les variables d'environnement `EMAIL_RECIPIENT`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USE_TLS`, `SMTP_USERNAME`, et `SMTP_PASSWORD` sont correctement définies (voir section "Configuration Générale").

- **Rappel :** Pour Gmail avec 2FA, utilisez un **Mot de passe d'application** pour `SMTP_PASSWORD`.
    
2.  **Test du Fonctionnement :**
    *   **Initialisation :** Exécutez le script de mise à jour une première fois :
        ```bash
        python data_sync
        ```
        *   Cela crée/met à jour la base de données et crée le fichier `db/last_known_ids.txt` contenant les IDs des contraventions actuelles. Aucun email n'est envoyé lors de cette première exécution car il n'y a pas d'état "précédent" à comparer.
    *   **Simulation de changements :**
        *   Ouvrez le fichier `db/last_known_ids.txt`.
        *   Supprimez manuellement quelques lignes et sauvegardez le fichier. 
    *   **Exécution  :**
        *   Ré-exécutez le script de mise à jour :
            ```bash
            python data_sync
            ```
        *   **Vérification :**
            *   **Console :** Vérifiez les logs à la console pour s'assurer du bon déroulement du processus.
            *   **Email :** Vérifiez la boîte de réception de l'adresse `email_recipient` configurée. L'email peut prendre quelques instants pour arriver. **Vérifiez également le dossier "Courrier indésirable/Junk.** 
            *   **Fichier `last_known_ids.txt` :** Vérifiez que ce fichier a été mis à jour.
    
---

## B2 - Publication Twitter des nouveaux établissements

Cette fonctionnalité publie sur Twitter les noms des établissements avec de nouvelles contraventions.

1.  **Configuration Préalable :**
    *   **Compte Développeur Twitter :** Un compte développeur Twitter est nécessaire ([developer.twitter.com](https://developer.twitter.com/)).
    *   **Application Twitter :** Créez une "App" dans le portail développeur associée au compte Twitter sur lequel vous souhaitez publier.
        *   Assurez-vous que l'App a les permissions **"Read and Write"** (Lecture et Écriture).
        *   Notez les 4 clés/jetons générés : **API Key, API Key Secret, Access Token, Access Token Secret**.
    *  **Variables d'Environnement :** 
        *   Assurez-vous que les variables d'environnement `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, et `TWITTER_ACCESS_TOKEN_SECRET` sont correctement définies (voir section "Configuration Générale").

2.  **Test du fonctionnement :**
    *   **Simulez de Nouvelles Contraventions :** Comme pour B1, exécutez `python data_sync` une fois, puis modifiez `db/last_known_ids.txt` en supprimant quelques lignes/IDs pour simuler des nouveautés.
    *   **Exécutez la Mise à Jour :**
        ```bash
        python data_sync
        ```
    *   **Vérification :**
        *   **Console :** Vérifiez les logs à la console pour s'assurer du bon déroulement du processus.
        *   **Compte Twitter :** Vérifiez si un nouveau tweet a été publié. Le tweet devrait commencer par "Nouvelle(s) contravention(s) détectée(s) pour : " suivi de la liste des noms uniques des établissements correspondant aux IDs que vous aviez supprimés de `last_known_ids.txt`.
      
---
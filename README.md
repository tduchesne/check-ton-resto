# INF5190 - Projet de session: Notes pour la correction

## A1 - Importation des données
Pour importer les données initiales dans la base de données :
1. Créez la base avec la commande suivante :
   ```bash
   sqlite3 db/violations.db < db/db.sql
   ```

2. Exécutez le script d'importation: 
    ```python
    python import_violations.py
    ```

## A2 - Outil de recherche
Lancez l'application avec: 
```bash
make run
```
- Accédez à http://127.0.0.1:5000/ pour utiliser la recherche 

 ## A3 - Background Scheduler

**Note importante** : En mode debug (`FLASK_DEBUG=1`), le reloader de Flask recharge `app.py`, ce qui entraîne une double initialisation du scheduler et des exécutions simultanées. Mettre `FLASK_DEBUG=0` au besoin.

## A4 - API RESTful
- `GET /contrevenants?du=<date>&au=<date>` : Liste les contraventions entre deux dates (ISO 8601, ex. `2022-05-08`). Retourne JSON avec code 200 ou 400.
- `GET /doc` : Affiche la documentation RAML en HTML (située dans `static/docs/doc.html`). Retourne code 200 si trouvé, 404 sinon.
- Testez avec :
  ```bash
  curl "http://127.0.0.1:5000/contrevenants?du=2022-05-08&au=2024-05-15"
  curl http://127.0.0.1:5000/doc
  ```
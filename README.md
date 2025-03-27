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
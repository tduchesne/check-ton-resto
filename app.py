from flask import Flask, g, render_template, request
from database import Database
import import_violations
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='static')

def init_scheduler():
    global scheduler
    scheduler = BackgroundScheduler()
    if not scheduler.get_job('update_db'):
        print("Ajout de la tâche de synchronisation...")
        scheduler.add_job(update_db, 'interval', days=1, id='update_db', replace_existing=True)
    if not scheduler.running:
        print("Démarrage du scheduler...")
        scheduler.start()


def update_db():
    print("Début de la synchronisation des violations...")
    try:
        import_violations.update_db()
        print("Synchronisation terminée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la synchronisation : {e}")   


init_scheduler()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close_connection()


@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        query = request.form.get('query')
        if search_type and query and len(query) >= 3:
            results = db.search_violation(search_type, query)
            return render_template('search_result.html', results=results, search_type=search_type, query=query)
        else: 
            return render_template("index.html", title= "Acceuil", error="La recherche doit contenir au moins 3 caractères.")
    return render_template("index.html", title="Accueil")


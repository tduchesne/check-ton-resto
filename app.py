from flask import Flask, g, json, jsonify, make_response, render_template, request
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
    error_search_violation = None
    # Rechercher des contraventions
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        query = request.form.get('query')
        if search_type and query and len(query) >= 3:
            results = db.search_violation(search_type, query)
            return render_template('search_result.html', results=results, search_type=search_type, query=query)
        else: 
            error_search_violation = "La recherche doit contenir au moins 3 caractères."
            return render_template("index.html", title= "Acceuil", error=error_search_violation)
        # Si méthode = GET
    return render_template("index.html", title="Accueil")


@app.route('/contrevenants', methods=['GET'])
def get_contraventions():
    """
    API endpoint pour obtenir toutes les infractions pour une période donnée.
    :return: Liste d'infractions au format JSON
    """
    db = get_db()
    start_date = request.args.get('du')
    end_date = request.args.get('au') 
    is_valid, error_message = validate_date_period(start_date, end_date)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    results = db.get_violations_by_date(start_date, end_date)
    # app.response_class gère l'encodage UTF-8 correctement
    return app.response_class(
        response=json.dumps(results, ensure_ascii=False),
        status=200,
        mimetype='application/json; charset=utf-8'
    )


@app.route('/doc', methods=['GET'])
def documentation():
    return app.send_static_file('docs/doc.html')


@app.route('/infractions/<path:establishment_name>', methods=['GET'])
def get_infractions_by_establishment_name(establishment_name):
    """
    API endpoint pour obternir toutes les infractions d'un établissement donné.
    Le nom de l'établissement est passé dans l'URL.
    :param establishment_name: Nom de l'établissement
    :return: Liste d'infractions au format JSON
    """
    db = get_db()
    start_date = request.args.get('du')
    end_date = request.args.get('au')
    is_valid, error_message = validate_date_period(start_date, end_date)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    results = db.get_infractions_by_establishment(establishment_name, start_date, end_date)
    if not results:
        return jsonify({"error": "Aucune infraction trouvée pour cet établissement. "}), 404
    return app.response_class(
        response=json.dumps(results, ensure_ascii=False),
        status=200,
        mimetype='application/json; charset=utf-8'
    )


def validate_date_period(start_date_str, end_date_str):
    """
    Valide une période de dates fournie sous forme de chaînes ISO 8601.
    param:
        start_date_str: Date de début (chaîne YYYY-MM-DD) ou None.
        end_date_str: Date de fin (chaîne YYYY-MM-DD) ou None.
    Returns:
        tuple: (is_valid, error_message)
               - (True, None) si la période est valide.
               - (False, "Message d'erreur") si la période est invalide.
    """
    if not start_date_str or not end_date_str:
        return False, "Les paramètres 'du' et 'au' sont requis."
    try:
        start_dt = datetime.fromisoformat(start_date_str)
        end_dt = datetime.fromisoformat(end_date_str)
    except ValueError:
        return False, "Les dates doivent être au format ISO 8601 (YYYY-MM-DD)."
    if start_dt > end_dt:
        return False, "La date de début doit être antérieure ou égale à la date de fin."
    return True, None


@app.route('/etablissements', methods=['GET'])
def get_sorted_establishments():
    """
    API endpoint pour obtenir une liste triée en ordre décroissant
    des établissements par nombre d'infractions.
    :return:Liste d'établissements au format JSON
    """
    db = get_db()
    try:
        establishments = db.get_establishments_by_infraction_count()
        assert establishments, "Aucun établissement trouvé."
        return jsonify(establishments)
    except Exception as e:
         print(f"Erreur lors de la récupération des établissements: {e}")
         return jsonify({"error": "Erreur interne du serveur"}), 500

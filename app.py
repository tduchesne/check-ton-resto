from flask import Flask, g, render_template, request
from .database import Database
app = Flask(__name__, static_url_path='', static_folder='static')


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

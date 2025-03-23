from flask import Flask, render_template
from database import Database


app = Flask(__name__, static_url_path='', static_folder='static')

@app.route('/')
def index(): 
    return render_template("index.html", title = "Accueil")

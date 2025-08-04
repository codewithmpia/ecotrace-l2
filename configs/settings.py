from pathlib import Path
import uuid

from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_minify import Minify

BASE_DIR = Path(__file__).resolve().parent.parent

# Dossier de templates
TEMPLATE_DIR = str(BASE_DIR / "assets/templates")

# Dossier de statiques
STATIC_DIR = str(BASE_DIR / "assets/static")

# URI de la base de données
DB_URI = f"sqlite:///{BASE_DIR}/db.sqlite3"

# Création de l'application Flask
app = Flask(
    __name__, 
    template_folder=TEMPLATE_DIR, 
    static_folder=STATIC_DIR
)

# Clé secrète pour la session
app.config["SECRET_KEY"] = str(uuid.uuid4())

# Configuration de la base de données
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Initialisation de Flask-Minify
Minify(app=app, html=True, js=True, cssless=True)

# Context processors
from .processors import (
    inject_total_users,
    inject_total_activities,
    inject_get_total_emissions,
)

app.context_processor(inject_total_users)
app.context_processor(inject_total_activities)
app.context_processor(inject_get_total_emissions)


# Gestion des erreurs
from .errors import (
    page_not_found,
    internal_server_error
)
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)

# Enregistrement des applications
from auth.apps import auth
from carbon.apps import carbon

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(carbon, url_prefix="/")

from auth.models import User
from carbon.models import EmissionFactor

# Initialisation de la base de données
@app.before_request
def create_all():
    db.create_all()

    # Vérifier si les facteurs d'émission existent déjà
    if EmissionFactor.query.count() == 0:
        # Ajouter des facteurs d'émission par défaut
        default_factors = [
            # Transport
            EmissionFactor(
                category='transport', 
                subcategory='voiture', 
                activity_name='Voiture essence', 
                unit='km', 
                co2_factor=0.192, 
                source='ADEME'
            ),
            EmissionFactor(
                category='transport', 
                subcategory='voiture', 
                activity_name='Voiture diesel', 
                unit='km', 
                co2_factor=0.173, 
                source='ADEME'
            ),
            EmissionFactor(
                category='transport', 
                subcategory='voiture', 
                activity_name='Voiture électrique', 
                unit='km', 
                co2_factor=0.02, 
                source='ADEME'
            ),
            EmissionFactor(
                category='transport', 
                subcategory='transport en commun', 
                activity_name='Bus', 
                unit='km', 
                co2_factor=0.103, 
                source='ADEME'
            ),
            EmissionFactor(
                category='transport', 
                subcategory='transport en commun', 
                activity_name='Train', 
                unit='km', 
                co2_factor=0.0056, 
                source='ADEME'
            ),
            EmissionFactor(
                category='transport', 
                subcategory='avion', 
                activity_name='Avion', 
                unit='km', 
                co2_factor=0.285, 
                source='ADEME'
            ),
            
            # Alimentation
            EmissionFactor(
                category='food', 
                subcategory='viande', 
                activity_name='Boeuf', 
                unit='kg', 
                co2_factor=27.0, 
                source='ADEME'
            ),
            EmissionFactor(
                category='food', 
                subcategory='viande', 
                activity_name='Poulet', 
                unit='kg', 
                co2_factor=5.15, 
                source='ADEME'
            ),
            EmissionFactor(
                category='food', 
                subcategory='viande', 
                activity_name='Porc', 
                unit='kg', 
                co2_factor=5.8, 
                source='ADEME'
            ),
            EmissionFactor(
                category='food', 
                subcategory='produits laitiers', 
                activity_name='Fromage', 
                unit='kg', 
                co2_factor=5.3, 
                source='ADEME'
            ),
            EmissionFactor(
                category='food', 
                subcategory='produits laitiers', 
                activity_name='Lait', 
                unit='L', 
                co2_factor=0.94, 
                source='ADEME'
            ),
            EmissionFactor(
                category='food', 
                subcategory='légumes', 
                activity_name='Légumes locaux de saison', 
                unit='kg', 
                co2_factor=0.5, 
                source='ADEME'
            ),
            EmissionFactor(
                category='food', 
                subcategory='légumes', 
                activity_name='Légumes importés ou hors saison', 
                unit='kg', 
                co2_factor=2.7, 
                source='ADEME'
            ),
            
            # Énergie
            EmissionFactor(
                category='energy', 
                subcategory='électricité', 
                activity_name='Électricité (mix français)', 
                unit='kWh', 
                co2_factor=0.057, 
                source='ADEME'
            ),
            EmissionFactor(
                category='energy', 
                subcategory='chauffage', 
                activity_name='Gaz naturel', 
                unit='kWh', 
                co2_factor=0.205, 
                source='ADEME'
            ),
            EmissionFactor(
                category='energy', 
                subcategory='chauffage', 
                activity_name='Fioul domestique', 
                unit='L', co2_factor=3.25, 
                source='ADEME'
            ),
            
            # Consommation
            EmissionFactor(
                category='consumption', 
                subcategory='vêtements', 
                activity_name='T-shirt', 
                unit='unité', 
                co2_factor=7.0, 
                source='ADEME'
            ),
            EmissionFactor(
                category='consumption', 
                subcategory='vêtements', 
                activity_name='Jean', 
                unit='unité', 
                co2_factor=25.0, 
                source='ADEME'
            ),
            EmissionFactor(
                category='consumption', 
                subcategory='électronique', 
                activity_name='Smartphone', 
                unit='unité', 
                co2_factor=80.0, 
                source='ADEME'
            ),
            EmissionFactor(
                category='consumption', 
                subcategory='électronique', 
                activity_name='Ordinateur portable', 
                unit='unité', 
                co2_factor=156.0, 
                source='ADEME'
            )
        ]
        
        db.session.bulk_save_objects(default_factors)
        db.session.commit()

# Configuration de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "La connexion est requise."

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

@app.before_request
def get_current_user():
    g.user = current_user
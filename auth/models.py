from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from configs.settings import db
from carbon.models import EmissionFactor


class User(db.Model, UserMixin):
    """Modèle pour les utilisateurs de l'application"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relations
    activities = db.relationship('Activity', backref='user', lazy=True)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.created_at = datetime.now(timezone.utc)

    def check_password(self, password2):
        """Vérifie le mot de passe de l'utilisateur"""
        return check_password_hash(self.password, password2)
        
    def get_total_emissions(self):
        """Calcule les émissions totales de l'utilisateur à ce jour"""
        total = 0
        for activity in self.activities:
            factor = EmissionFactor.query.get(activity.emission_factor_id)
            total += activity.quantity * factor.co2_factor
            
        return total
    
    @classmethod
    def get_all_users_total_emissions(cls, with_unit=True):
        """
        Retourne les émissions totales de tous les utilisateurs, formatées (ex: 1.2 ktCO2, 950 tCO2, 500 kgCO2).
        Cette méthode calcule pour tous les utilisateurs, indépendamment de la connexion.
        """
        total = 0
        for user in cls.query.all():
            total += user.get_total_emissions()
        total = round(total, 2)
        if with_unit:
            if total >= 1_000_000:
                return f"{round(total/1_000_000, 2)} MtCO2"
            elif total >= 1_000:
                return f"{round(total/1_000, 2)} ktCO2"
            elif total >= 1:
                return f"{round(total, 2)} tCO2"
            else:
                return f"{round(total*1000, 2)} kgCO2"
        return total
    
    @classmethod
    def get_total_users(cls, formatted=False):
        """Retourne le nombre total d'utilisateurs, formaté si demandé (ex: 1, 10, 1K+, 10K+)"""
        count = cls.query.count()
        if formatted:
            if count >= 10_000:
                return f"{count // 1000}K+"
            elif count >= 1_000:
                return f"{count // 1000}K+"
            else:
                return str(count)
        return count
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True
    
    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
    
    def __str__(self):
        return self.name

from datetime import datetime, timezone

from configs.settings import db 


class EmissionFactor(db.Model):
    """Modèle pour les facteurs d'émission de CO2"""
    __tablename__ = 'emission_factors'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=False)
    activity_name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    co2_factor = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100))
    
    # Relations
    activities = db.relationship('Activity', backref='emission_factor', lazy=True)
        
    def __repr__(self):
        return f"<EmissionFactor {self.category}/{self.activity_name}: {self.co2_factor} {self.unit}>"
    
    @classmethod
    def get_by_category(cls, category):
        """Récupère tous les facteurs d'émission d'une catégorie donnée"""
        return cls.query.filter_by(category=category).all()
    
    

class Activity(db.Model):
    """Modèle pour les activités générant des émissions de CO2"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    emission_factor_id = db.Column(db.Integer, db.ForeignKey('emission_factors.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc).date())
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Activity {self.id} - User {self.user_id}>"
        
    def get_emissions(self):
        """Calcule les émissions pour cette activité"""
        factor = EmissionFactor.query.get(self.emission_factor_id)
        return self.quantity * factor.co2_factor
    
    @classmethod
    def get_total_activities(cls):
        """Retourne le nombre total d'activités, formaté (ex: 1, 1K, 1.2K)"""
        count = cls.query.count()
        if count < 1000:
            return str(count)
        elif count < 1_000_000:
            return f"{count/1000:.1f}K".rstrip('0').rstrip('.')
        else:
            return f"{count/1_000_000:.1f}M".rstrip('0').rstrip('.')
    
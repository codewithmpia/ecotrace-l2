# controllers/calculator.py
from datetime import datetime, timedelta
import calendar

from carbon.models import Activity, EmissionFactor


class CarbonCalculator:
    """Classe pour calculer l'empreinte carbone des utilisateurs"""
    
    def __init__(self, user_id):
        """Initialisation avec l'ID utilisateur"""
        self.user_id = user_id

    def calculate_daily_footprint(self, date):
        """
        Calcule l'empreinte carbone pour un jour spécifique
        
        Args:
            date: Date pour laquelle calculer l'empreinte
            
        Returns:
            dict: Empreinte totale et répartition par catégorie
        """
        # Récupérer toutes les activités de l'utilisateur pour ce jour
        activities = Activity.query.filter_by(
            user_id=self.user_id,
            date=date
        ).all()
        
        # Initialiser les compteurs
        total_emissions = 0
        by_category = {
            'transport': 0,
            'food': 0,
            'energy': 0,
            'consumption': 0
        }
        
        # Calculer les émissions pour chaque activité
        for activity in activities:
            # Vérifier si emission_factor_id existe
            if activity.emission_factor_id is None:
                continue
                
            # Récupérer le facteur d'émission
            emission_factor = EmissionFactor.query.get(activity.emission_factor_id)
            
            # Vérifier si le facteur d'émission existe
            if emission_factor is None:
                continue
            
            # Vérifier si la catégorie est valide
            if emission_factor.category not in by_category:
                continue
            
            # Calculer les émissions
            try:
                emissions = activity.quantity * emission_factor.co2_factor
            except Exception as e:
                continue
            
            # Ajouter au total
            total_emissions += emissions
            
            # Ajouter à la catégorie correspondante
            by_category[emission_factor.category] += emissions
        
        # Arrondir les valeurs pour l'affichage
        for category in by_category:
            by_category[category] = round(by_category[category], 2)
        
        return {
            'total': total_emissions,
            'by_category': by_category
        }

    def calculate_weekly_trend(self):
        """
        Calcule la tendance des émissions sur les 7 derniers jours
        
        Returns:
            list: Liste de dictionnaires avec la date et les émissions
        """
        today = datetime.now().date()
        start_date = today - timedelta(days=6)  # 7 jours au total
        
        # Liste pour stocker les résultats
        daily_emissions = []
        
        # Calculer les émissions pour chaque jour
        current_date = start_date

        while current_date <= today:
            result = self.calculate_daily_footprint(current_date)
            daily_emissions.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'display_date': current_date.strftime('%d/%m'),
                'emissions': round(result['total'], 2)
            })
            current_date += timedelta(days=1)
        
        return daily_emissions
    
    def calculate_monthly_summary(self, month=None, year=None):
        """
        Calcule le résumé des émissions pour un mois donné
        
        Args:
            month: Mois (1-12, par défaut mois actuel)
            year: Année (par défaut année actuelle)
            
        Returns:
            dict: Résumé des émissions pour le mois
        """
        # Si mois/année non spécifiés, utiliser le mois actuel
        if month is None or year is None:
            now = datetime.now()
            month = month or now.month
            year = year or now.year
        
        # Déterminer le premier et le dernier jour du mois
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()
        
        # Récupérer toutes les activités du mois
        activities = Activity.query.filter(
            Activity.user_id == self.user_id,
            Activity.date >= first_day,
            Activity.date <= last_day
        ).all()
        
        # Initialiser les compteurs
        total_emissions = 0
        by_category = {
            'transport': 0,
            'food': 0,
            'energy': 0,
            'consumption': 0
        }
        
        # Calculer les émissions pour chaque activité
        for activity in activities:
            emission_factor = EmissionFactor.query.get(activity.emission_factor_id)
            emissions = activity.quantity * emission_factor.co2_factor
            
            # Ajouter au total
            total_emissions += emissions
            
            # Ajouter à la catégorie correspondante
            by_category[emission_factor.category] += emissions
        
        # Calculer la moyenne journalière
        days_in_month = (last_day - first_day).days + 1
        daily_average = total_emissions / days_in_month if days_in_month > 0 else 0
        
        return {
            'total': round(total_emissions, 2),
            'daily_average': round(daily_average, 2),
            'by_category': {cat: round(val, 2) for cat, val in by_category.items()}
        }
    
    def compare_with_average(self):
        """
        Compare l'empreinte de l'utilisateur avec la moyenne nationale
        
        Returns:
            dict: Comparaison en pourcentage
        """
        # Moyenne nationale (en kg CO2 par jour) - valeurs fictives pour l'exemple
        national_average = {
            'total': 12.0,  # Moyenne totale
            'transport': 5.0,
            'food': 3.5,
            'energy': 2.0,
            'consumption': 1.5
        }
        
        # Calculer l'empreinte de l'utilisateur pour aujourd'hui
        today = datetime.now().date()
        user_footprint = self.calculate_daily_footprint(today)
        
        # Calculer le pourcentage par rapport à la moyenne
        comparison = {}
        
        # Total
        if national_average['total'] > 0:
            comparison['total'] = (user_footprint['total'] / national_average['total']) * 100
        else:
            comparison['total'] = 0
            
        # Par catégorie
        comparison['by_category'] = {}
        
        for category in user_footprint['by_category']:
            if national_average[category] > 0:
                comparison['by_category'][category] = (user_footprint['by_category'][category] / national_average[category]) * 100
            else:
                comparison['by_category'][category] = 0
        
        return {
            'national_average': national_average,
            'user_footprint': user_footprint,
            'percentage': {k: round(v, 1) for k, v in comparison.items() if k != 'by_category'},
            'percentage_by_category': {k: round(v, 1) for k, v in comparison['by_category'].items()}
        }



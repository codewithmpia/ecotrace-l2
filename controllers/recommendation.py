# controllers/recommendation.py
from datetime import datetime, timedelta
from carbon.models import Activity, EmissionFactor


class RecommendationEngine:
    """Moteur de recommandations pour réduire l'empreinte carbone"""
    
    def __init__(self, user_id):
        """Initialisation avec l'ID utilisateur"""
        self.user_id = user_id
        
    def get_personalized_recommendations(self):
        """
        Génère des recommandations personnalisées basées sur l'historique de l'utilisateur
        
        Returns:
            list: Liste de recommandations
        """
        try:
            # Récupérer les activités récentes (30 derniers jours)
            today = datetime.now().date()
            start_date = today - timedelta(days=30)
            
            recent_activities = Activity.query.filter(
                Activity.user_id == self.user_id,
                Activity.date >= start_date
            ).all()
            
            # Si pas assez de données, retourner des recommandations génériques
            if len(recent_activities) < 5:
                return self._get_generic_recommendations()
            
            # Analyser les données pour identifier les domaines d'amélioration
            emissions_by_category = {
                'transport': 0,
                'food': 0,
                'energy': 0,
                'consumption': 0
            }
            
            # Calculer les émissions par catégorie
            for activity in recent_activities:
                # Vérifier si emission_factor_id existe et est valide
                if activity.emission_factor_id is None:
                    continue
                    
                # Récupérer le facteur d'émission
                emission_factor = EmissionFactor.query.get(activity.emission_factor_id)
                
                # Vérifier si le facteur d'émission existe
                if emission_factor is None:
                    continue
                
                # Vérifier si la catégorie est valide
                if emission_factor.category not in emissions_by_category:
                    continue
                
                # Calculer les émissions
                try:
                    emissions = activity.quantity * emission_factor.co2_factor
                    emissions_by_category[emission_factor.category] += emissions

                except Exception as e:
                    continue
            
            # Identifier la catégorie avec le plus d'émissions
            if all(value == 0 for value in emissions_by_category.values()):
                # Si toutes les catégories sont à 0, retourner des recommandations génériques
                return self._get_generic_recommendations()
                
            max_category = max(emissions_by_category.items(), key=lambda x: x[1])[0]
            
            # Générer des recommandations spécifiques pour cette catégorie
            category_recommendations = self._get_category_recommendations(max_category)
            
            # Ajouter quelques recommandations génériques
            generic_recommendations = self._get_generic_recommendations()[:2]
            
            # Combiner les recommandations
            all_recommendations = category_recommendations + generic_recommendations
            
            return all_recommendations
        
        except Exception as e:
            # En cas d'erreur, retourner des recommandations génériques
            return self._get_generic_recommendations()
    
    def _get_category_recommendations(self, category):
        """
        Génère des recommandations spécifiques à une catégorie
        
        Args:
            category: Catégorie pour laquelle générer des recommandations
            
        Returns:
            list: Liste de recommandations pour cette catégorie
        """
        recommendations = []
        
        if category == 'transport':
            recommendations = [
                {
                    'title': 'Réduisez vos déplacements en voiture',
                    'description': 'Essayez de combiner plusieurs courses en un seul trajet pour réduire votre kilométrage hebdomadaire.',
                    'impact': 'Moyen',
                    'ease': 'Facile'
                },
                {
                    'title': 'Utilisez plus les transports en commun',
                    'description': 'Remplacer un trajet en voiture par les transports en commun peut réduire vos émissions de CO2 jusqu\'à 80%.',
                    'impact': 'Élevé',
                    'ease': 'Moyen'
                },
                {
                    'title': 'Essayez le covoiturage',
                    'description': 'Partager votre trajet avec d\'autres personnes divise les émissions par le nombre de passagers.',
                    'impact': 'Élevé',
                    'ease': 'Moyen'
                }
            ]
        elif category == 'food':
            recommendations = [
                {
                    'title': 'Réduisez votre consommation de viande rouge',
                    'description': 'Remplacer la viande rouge par de la volaille peut réduire vos émissions alimentaires de plus de 70%.',
                    'impact': 'Très élevé',
                    'ease': 'Moyen'
                },
                {
                    'title': 'Privilégiez les produits locaux et de saison',
                    'description': 'Les légumes importés ou hors saison peuvent émettre jusqu\'à 5 fois plus de CO2 que les produits locaux de saison.',
                    'impact': 'Moyen',
                    'ease': 'Facile'
                },
                {
                    'title': 'Réduisez le gaspillage alimentaire',
                    'description': 'Planifiez vos repas et utilisez les restes pour éviter de jeter de la nourriture.',
                    'impact': 'Moyen',
                    'ease': 'Facile'
                }
            ]
        elif category == 'energy':
            recommendations = [
                {
                    'title': 'Réduisez votre chauffage de 1°C',
                    'description': 'Baisser la température de votre logement de 1°C peut réduire votre consommation d\'énergie de 7%.',
                    'impact': 'Moyen',
                    'ease': 'Très facile'
                },
                {
                    'title': 'Éteignez les appareils en veille',
                    'description': 'Les appareils en veille peuvent représenter jusqu\'à 10% de votre facture d\'électricité.',
                    'impact': 'Faible',
                    'ease': 'Très facile'
                },
                {
                    'title': 'Installez des ampoules LED',
                    'description': 'Les ampoules LED consomment jusqu\'à 80% d\'électricité en moins que les ampoules à incandescence.',
                    'impact': 'Faible',
                    'ease': 'Facile'
                }
            ]
        elif category == 'consumption':
            recommendations = [
                {
                    'title': 'Allongez la durée de vie de vos appareils électroniques',
                    'description': 'La fabrication d\'un smartphone représente environ 80% de son impact environnemental total.',
                    'impact': 'Élevé',
                    'ease': 'Moyen'
                },
                {
                    'title': 'Achetez des vêtements de seconde main',
                    'description': 'L\'industrie textile est la 2ème plus polluante au monde. Privilégiez les vêtements d\'occasion.',
                    'impact': 'Moyen',
                    'ease': 'Facile'
                },
                {
                    'title': 'Réparez au lieu de remplacer',
                    'description': 'Réparer un objet plutôt que d\'en acheter un neuf peut réduire significativement votre empreinte carbone.',
                    'impact': 'Élevé',
                    'ease': 'Moyen'
                }
            ]
        
        # Retourner les 3 meilleures recommandations pour cette catégorie
        return recommendations
    
    def _get_generic_recommendations(self):
        """
        Génère des recommandations génériques adaptées à tous les utilisateurs
        
        Returns:
            list: Liste de recommandations génériques
        """
        return [
            {
                'title': 'Privilégiez les déplacements doux',
                'description': 'Marcher ou faire du vélo pour les courtes distances est bon pour la santé et pour la planète.',
                'impact': 'Moyen',
                'ease': 'Facile'
            },
            {
                'title': 'Réduisez votre consommation de viande',
                'description': 'Essayez d\'introduire une journée sans viande par semaine dans votre alimentation.',
                'impact': 'Élevé',
                'ease': 'Moyen'
            },
            {
                'title': 'Éteignez les lumières inutiles',
                'description': 'Cette simple habitude peut réduire votre consommation d\'électricité jusqu\'à 5%.',
                'impact': 'Faible',
                'ease': 'Très facile'
            },
            {
                'title': 'Limitez les achats en ligne avec livraison express',
                'description': 'Les livraisons express génèrent plus d\'émissions que les livraisons standard qui permettent d\'optimiser les trajets.',
                'impact': 'Moyen',
                'ease': 'Facile'
            },
            {
                'title': 'Utilisez des sacs réutilisables',
                'description': 'Évitez les sacs en plastique à usage unique lors de vos courses.',
                'impact': 'Faible',
                'ease': 'Très facile'
            }
        ]
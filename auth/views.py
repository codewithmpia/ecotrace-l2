import json
from datetime import datetime

from flask import (
    render_template, 
    session,
    redirect, 
    url_for, 
    flash,
    request
)
from flask.views import MethodView
from flask_login import (
    logout_user,
    login_required,
    login_user,
    current_user
)

from configs.errors import get_form_errors
from controllers.calculator import CarbonCalculator
from controllers.recommentation import RecommendationEngine
from carbon.models import EmissionFactor, Activity

from .forms import (
    RegistrationForm, 
    LoginForm
)
from .models import db, User


class RegisterView(MethodView):
    """
    Vue pour l'inscription des utilisateurs.
    Cette vue gère l'affichage du formulaire d'inscription,
    la validation des données soumises et la création d'un nouvel utilisateur.
    """
    template_name = "auth/register.html"
    form_class = RegistrationForm

    def get(self):
        if current_user.is_authenticated:
            # Si l'utilisateur est déjà connecté, 
            # redirigez-le vers le tableau de bord
            flash("Vous êtes déjà connecté.", "info")
            return redirect(url_for('auth.dashboard'))
            
        form = self.form_class()

        ctx = {
            "title": "Inscription",
            "form": form
        }
        return render_template(self.template_name, **ctx)
    
    def post(self):
        form = self.form_class()

        if form.validate_on_submit():
            name=form.name.data
            email=form.email.data
            password=form.password.data

            # Vérifier si l'utilisateur existe déjà
            existing_user = User.query.filter_by(email=email).first()
            
            if existing_user:
                flash("Un utilisateur avec cet email existe déjà.", "error")
                return redirect(url_for('auth.register'))
            
            new_user = User(
                name=name,
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for('auth.login'))
        
        elif form.errors:
            get_form_errors(form)
            
        ctx = {
            "title": "Inscription",
            "form": form
        }
        return render_template(self.template_name, **ctx)
    

class LoginView(MethodView):
    """
    Vue pour la connexion des utilisateurs.
    Cette vue gère l'affichage du formulaire de connexion,
    la validation des données soumises et l'authentification de l'utilisateur.
    """
    template_name = "auth/login.html"
    form_class = LoginForm

    def get(self):
        if current_user.is_authenticated:
            # Si l'utilisateur est déjà connecté, 
            # redirigez-le vers le tableau de bord
            flash("Vous êtes déjà connecté.", "info")
            return redirect(url_for('auth.dashboard'))
            
        form = self.form_class()

        ctx = {
            "title": "Connexion",
            "form": form
        }
        return render_template(self.template_name, **ctx)
    
    def post(self):
        form = self.form_class()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(
                    user, 
                    remember=form.remember.data
                )
                next_page = request.args.get('next')
                flash("Connexion réussie !", "success")
                return redirect(next_page or url_for('auth.dashboard'))
            else:
                flash("Email ou mot de passe incorrect.", "error")

        elif form.errors:
            get_form_errors(form)
                
        ctx = {
            "title": "Connexion",
            "form": form
        }
        return render_template(self.template_name, **ctx)
    

class LogoutView(MethodView):
    """
    Vue pour la déconnexion des utilisateurs.
    Cette vue gère la déconnexion de l'utilisateur et le redirige vers la page d'accueil ou vers la page de connexion.
    """
    decorators = [login_required]
    
    def get(self):
        logout_user()
        flash("Déconnexion réussie !", "info")
        session.pop("user_id", None)
        return redirect(url_for("carbon.index")) or redirect(url_for("auth.login"))
    

class DashboardView(MethodView):
    """
    Vue pour le tableau de bord des utilisateurs.
    Cette vue affiche les informations de l'utilisateur connecté,
    y compris les données des émissions de carbone.
    """
    template_name = "auth/dashboard.html"
    decorators = [login_required]

    def get(self):
        user = current_user
        user_id = user.id if user.is_authenticated else session.get("user_id")

        if not user_id:
            flash("Vous devez être connecté pour accéder au tableau de bord.", "warning")
            return redirect(url_for("auth.login"))
        
        # Créer les calculateurs 
        calculator = CarbonCalculator(user_id)
        recommendation_engine = RecommendationEngine(user_id)

        # Obtenir les données avec la gestion des erreurs
        today = datetime.now().date()

        try:
            # Essayer de calculer l'empreinte quotidienne
            daily_footprint = calculator.calculate_daily_footprint(today)

        except Exception as e:
            # En cas d'erreur, utiliser des valeurs par défaut
            daily_footprint = {
                'total': 0,
                'by_category': {
                    'transport': 0,
                    'food': 0,
                    'energy': 0,
                    'consumption': 0
                }
            }
        
        try:
            # Essayer de calculer la tendance hebdomadaire
            weekly_trend = calculator.calculate_weekly_trend()
            weekly_trend_json = json.dumps(weekly_trend)

        except Exception as e:
            # En cas d'erreur, utiliser des valeurs par défaut
            weekly_trend = []
            weekly_trend_json = "[]"

        try:
            # Essayer de calculer le résumé mensuel
            monthly_summary = calculator.calculate_monthly_summary()
            monthly_summary_json = json.dumps(monthly_summary)
        except Exception as e:
            # En cas d'erreur, utiliser des valeurs par défaut
            monthly_summary = []
            monthly_summary_json = "[]" 
        
        try:
            # Essayer d'obtenir les recommandations
            recommendations = recommendation_engine.get_personalized_recommendations()

        except Exception as e:
            # En cas d'erreur, utiliser des valeurs par défaut
            recommendations = []
    
        # Convertir les données pour JavaScript
        try:
            categories_json = json.dumps(daily_footprint['by_category'])
        
        except Exception as e:
            # En cas d'erreur, utiliser une chaîne vide
            categories_json = "{}"

        # Récupérer les 3 dernières activités de l'utilisateur
        activities = Activity.query.filter_by(user_id=user.id).order_by(Activity.date.desc()).limit(3).all()

        # Préparer les données pour l'affichage
        activities_data = []

        for activity in activities:
            emission_factor = EmissionFactor.query.get(activity.emission_factor_id)
            activities_data.append({
                'id': activity.id,
                'date': activity.date,
                'category': emission_factor.category,
                'name': emission_factor.activity_name,
                'quantity': activity.quantity,
                'unit': emission_factor.unit,
                'emissions': round(activity.quantity * emission_factor.co2_factor, 2)
            })

        ctx = {
            "title": "Tableau de bord",
            "user": current_user,
            "total_emissions": current_user.get_total_emissions(),
            "daily_total": round(daily_footprint.get("total", 0), 2),
            "daily_by_category": daily_footprint.get("by_category", {}),
            "daily_footprint": daily_footprint,

            "weekly_trend": weekly_trend_json,
            "categories_data": categories_json,
            "monthly_summary": monthly_summary_json,

            "recommendations": recommendations,
            "activities": activities_data,
        }
        return render_template(self.template_name, **ctx)
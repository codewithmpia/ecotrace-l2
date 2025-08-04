from datetime import datetime
from functools import lru_cache
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask.views import MethodView
from flask_login import (
    login_required,
    current_user,
)
from .models import (
    db,
    EmissionFactor, 
    Activity
)
from .forms import AddActivityForm


class IndexView(MethodView):
    template_name = "carbon/index.html"

    def get(self):
        ctx = {
            "title": "Accueil"
        }
        return render_template(self.template_name, **ctx)


class AddActivityView(MethodView):
    template_name = "carbon/add_activity.html"
    form_class = AddActivityForm
    decorators = [login_required]
    
    VALID_CATEGORIES = {"transport", "food", "energy", "consumption"}

    @lru_cache(maxsize=128)
    def _get_emission_factors(self):
        """Cache des facteurs d'émission pour éviter les requêtes répétées"""
        return {
            category: EmissionFactor.query.filter_by(category=category).all()
            for category in self.VALID_CATEGORIES
        }

    def _get_context(self):
        """Contexte réutilisable pour le template"""
        factors = self._get_emission_factors()
        return {
            "title": "Ajouter une activité",
            "transport_factors": factors["transport"],
            "food_factors": factors["food"],
            "energy_factors": factors["energy"],
            "consumption_factors": factors["consumption"],
            "today": datetime.now().date(),
        }

    def _validate_form_data(self, form_data):
        """Validation centralisée avec retour d'erreurs et de données"""
        errors = []
        validated_data = {}

        # Validation catégorie
        category = form_data.get("category", "").strip()
        if not category:
            errors.append("Veuillez sélectionner une catégorie.")
        elif category not in self.VALID_CATEGORIES:
            errors.append(f"Catégorie '{category}' non valide.")
        else:
            validated_data["category"] = category

        # Validation activité
        activity_id = form_data.get("activity_id", "").strip()
        if not activity_id:
            errors.append("Veuillez sélectionner une activité spécifique.")
        else:
            try:
                activity_id = int(activity_id)
                emission_factor = EmissionFactor.query.get(activity_id)
                if not emission_factor:
                    errors.append(f"L'activité sélectionnée n'existe pas.")
                else:
                    validated_data["emission_factor"] = emission_factor
            except ValueError:
                errors.append("Identifiant d'activité invalide.")

        # Validation quantité
        quantity_str = form_data.get("quantity", "").strip()
        if not quantity_str:
            errors.append("Veuillez saisir une quantité.")
        else:
            try:
                quantity = float(quantity_str)
                if quantity <= 0:
                    errors.append("La quantité doit être supérieure à zéro.")
                else:
                    validated_data["quantity"] = quantity
            except ValueError:
                errors.append("La quantité n'est pas un nombre valide.")

        # Validation date
        date_str = form_data.get("date", "").strip()
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
            validated_data["date"] = date
        except ValueError:
            errors.append("Format de date invalide.")

        return errors, validated_data

    def _flash_errors(self, errors):
        """Flash des erreurs de manière groupée"""
        for error in errors:
            flash(error, "danger")

    def _create_activity(self, validated_data):
        """Création sécurisée de l'activité"""
        try:
            activity = Activity(
                user_id=current_user.id,
                emission_factor_id=validated_data["emission_factor"].id,
                quantity=validated_data["quantity"],
                date=validated_data["date"]
            )
            db.session.add(activity)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            flash("Une erreur s'est produite lors de l'ajout de l'activité.", "danger")
            return False

    def get(self):
        """Affichage du formulaire"""
        return render_template(self.template_name, **self._get_context())
    
    def post(self):
        """Traitement du formulaire"""
        # Validation des données
        errors, validated_data = self._validate_form_data(request.form)
        
        if errors:
            self._flash_errors(errors)
            return render_template(self.template_name, **self._get_context())
        
        # Création de l'activité
        if self._create_activity(validated_data):
            flash("Activité ajoutée avec succès !", "success")
            return redirect(url_for("carbon.add_activity"))
        
        # En cas d'erreur de création
        return render_template(self.template_name, **self._get_context())
    

class HistoryView(MethodView):
    template_name = "carbon/history.html"
    decorators = [login_required]

    def get(self):
        """Affichage de l'historique des activités"""
        user = current_user
        
        if not user:
            flash("Vous devez être connecté pour voir votre historique.", "warning")
            return redirect(url_for("auth.login"))
        
        # Récupération des activités de l'utilisateur
        activities = (
            Activity.query
            .filter_by(user_id=current_user.id)
            .order_by(Activity.date.desc())
            .all()
        )

        # Préparation des données pour la contruction de graphiques
        activities_data = []

        for activity in  activities:
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
        # Contexte pour le template
        ctx = {
            "title": "Historique des activités",
            "activities": activities,
            "activities_json": activities_data,
        }
        return render_template(self.template_name, **ctx)
    


class DeleteActivityView(MethodView):
    decorators = [login_required]

    def post(self, activity_id):
        """Suppression d'une activité"""
        user = current_user

        if not user:
            flash("Vous devez être connecté pour supprimer une activité.", "warning")
            return redirect(url_for("auth.login"))
        
        # Vérification de l'existence de l'activité et appartient # à l'utilisateur
        activity = Activity.query.filter_by(
            id=activity_id, 
            user_id=user.id
        ).first()

        if not activity:
            flash("Activité non trouvée ou vous n'avez pas la permission de la supprimer.", "danger")
            return redirect(url_for("carbon.history"))
        try:
            db.session.delete(activity)
            db.session.commit()
            flash("Activité supprimée avec succès !", "success")
            
        except Exception as e:
            db.session.rollback()
            flash("Une erreur s'est produite lors de la suppression de l'activité.", "danger")

        return redirect(request.referrer) or redirect(url_for("carbon.history"))
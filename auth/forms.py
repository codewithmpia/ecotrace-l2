from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    name = StringField('Nom', validators=[
        DataRequired(message="Le nom est requis"),
        Length(min=2, max=100, message="Le nom doit contenir entre 2 et 100 caractères")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="L'email est requis"),
        Email(message="Veuillez entrer une adresse email valide")
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message="Le mot de passe est requis"),
        Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères")
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message="La confirmation du mot de passe est requise"),
        EqualTo('password', message="Les mots de passe ne correspondent pas")
    ])
    submit = SubmitField("S'inscrire")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Cette adresse email est déjà utilisée")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="L'email est requis"),
        Email(message="Veuillez entrer une adresse email valide")
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message="Le mot de passe est requis")
    ])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

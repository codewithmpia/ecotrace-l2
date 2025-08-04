from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField,
    DateField,
    SelectField,
    FloatField
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Optional,
)


class AddActivityForm(FlaskForm):
    category = SelectField(
        label="Catégorie",
        choices=[
            ("", "Sélectionnez une catégorie"),
            ("transport", "Transport"),
            ("food", "Alimentation"),
            ("energy", "Énergie"),
            ("consumption", "Consommation"),
        ],
        validators=[DataRequired(message="Le champ catégorie est requis")],
    )
    activity_id = SelectField(
        label="Type d'activité",
        choices=[],  # Les choix seront remplis dynamiquement
        validators=[Optional()],
    )
    quantity = FloatField(
        label="Quantité",
        validators=[
            DataRequired(message="Le champ quantité est requis"),
            NumberRange(min=0, message="La quantité doit être positive"),
        ],
    )
    date = DateField(
        label="Date",
        format="%Y-%m-%d",
        validators=[DataRequired(message="Le champ date est requis")],
    )
    submit = StringField(label="Ajouter l'activité")

from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, StringField
from wtforms.validators import DataRequired, NumberRange


class CagnotteForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(message="Le nom est requis.")])


class DepenseForm(FlaskForm):
    participant = StringField(
        "Participant",
        validators=[DataRequired(message="Le participant est requis.")],
    )
    montant = FloatField(
        "Montant (€)",
        validators=[
            DataRequired(message="Le montant est requis."),
            NumberRange(min=0.01, message="Le montant doit être positif."),
        ],
    )
    date_paiement = DateField(
        "Date",
        default=date.today,
        validators=[DataRequired(message="La date est requise.")],
    )

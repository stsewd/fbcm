from pony.orm import db_session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, ValidationError

from .models import Player


def only_alpha(form, field):
    attr = field.data
    if not attr.replace(" ", "").isalpha():
        raise ValidationError(
            "El atributo {name} contiene caracteres no válidos".format(
                name=field.label.text.lower()
            )
        )


class PlayerForm(FlaskForm):
    id = StringField('ID', validators=[
        DataRequired(message="ID faltante."),
        Length(min=10, max=10, message="El id debe tener 10 dígitos.")
    ])

    name = StringField('Nombre', validators=[
        DataRequired(message="Nombre faltante."),
        only_alpha,
        Length(max=40, message="Nombre demasiado largo.")
    ])

    lastname = StringField('Apellido', validators=[
        DataRequired(message="Apellido faltante."),
        only_alpha,
        Length(max=40, message="Apellido demasiado largo.")
    ])

    def validate_id(form, field):
        error = ""
        id = field.data
        if not id.isdigit():
            error = "El id debe contener sólo números."
        elif PlayerForm._player_exists(id):
            error = "El jugador ya existe."
        if error:
            raise ValidationError(error)

    @staticmethod
    @db_session
    def _player_exists(id):
        return Player.exists(id=id)

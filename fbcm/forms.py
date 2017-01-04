from pony.orm import db_session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from .models import Player, Team, Championship


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


class TeamForm(FlaskForm):
    name = StringField('Nombre', validators=[
        DataRequired(message="Nombre faltante."),
        Length(max=90, message="Nombre demasiado largo.")
    ])

    def validate_name(form, field):
        error = ""
        name = field.data
        if TeamForm._team_exists(name):
            error = "El nombre ya está ocupado."
        if error:
            raise ValidationError(error)

    @staticmethod
    @db_session
    def _team_exists(name):
        return Team.exists(name=name)


class ChampionshipForm(FlaskForm):
    name = StringField('Nombre', validators=[
        DataRequired(message="Nombre faltante."),
        Length(max=90, message="Nombre demasiado largo.")
    ])
    description = TextAreaField('Descripción', validators=[
        Length(max=500, message="Descripción demasiada larga.")
    ])

    def validate_name(form, field):
        error = ""
        name = field.data
        if ChampionshipForm._championship_exists(name):
            error = "El nombre ya está ocupado."
        if error:
            raise ValidationError(error)

    @staticmethod
    @db_session
    def _championship_exists(name):
        return Championship.exists(name=name)

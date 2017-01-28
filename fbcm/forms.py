from pony.orm import db_session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

from .models import Player, Team, Championship, Position


def only_alpha(form, field):
    attr = field.data
    if not attr.replace(" ", "").isalpha():
        raise ValidationError(
            "El atributo {name} contiene caracteres no válidos".format(
                name=field.label.text.lower()
            )
        )


@db_session
def get_positions():
    return [
        (str(p.id), p.name)
        for p in Position.select()
    ]


class PlayerForm(FlaskForm):
    class Meta:
        csrf = False

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
    class Meta:
        csrf = False

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


class AddPlayerToTeamForm(FlaskForm):
    class Meta:
        csrf = False

    player_id = StringField("ID", validators=[
        DataRequired(message="ID faltante.")
    ])

    number = StringField('Número', validators=[
        DataRequired(message="Número del jugador faltante.")
    ])

    position = SelectField(
        'Posición',
        validators=[
            DataRequired(message="Posición del jugador faltante.")
        ],
        choices=get_positions()
    )

    def validate_player_id(form, field):
        error = ""
        id = field.data
        if not PlayerForm._player_exists(id):
            error = "El jugador no existe."
        if error:
            raise ValidationError(error)


class ChampionshipForm(FlaskForm):
    class Meta:
        csrf = False

    name = StringField('Nombre', validators=[
        DataRequired(message="Nombre faltante."),
        Length(max=90, message="Nombre demasiado largo.")
    ])
    description = TextAreaField(
        'Descripción',
        validators=[
            Length(max=500, message="Descripción demasiada larga.")
        ],
        render_kw={
            'placeholder': "Descripción opcional."
        }
    )

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


class AddTeamToChampionshipForm(FlaskForm):
    class Meta:
        csrf = False

    team_name = StringField("Equipo", validators=[
        DataRequired(message="Equipo faltante.")
    ])

    def validate_team_name(form, field):
        error = ""
        name = field.data
        if not TeamForm._team_exists(name):
            error = "El equipo no existe."
        if error:
            raise ValidationError(error)


class GoalForm(FlaskForm):
    class Meta:
        csrf = False

    team = SelectField(
        'Equipo',
        validators=[
            DataRequired(message="Equipo faltante.")
        ],
        coerce=int
    )

    player = StringField('Jugador', validators=[
        DataRequired(message="Jugador faltante.")
    ])

    def __init__(self, match):
        FlaskForm.__init__(self)
        self.team.choices = [
            (tm.team.team.id, tm.team.team.name)
            for tm in match.team_matches
        ]

    def validate_player(form, field):
        pass  # TODO

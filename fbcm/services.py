from pony.orm import db_session

from .models import Player


class FbcmError(Exception):
    def __init__(self, msg, status_code=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.status_code = status_code if status_code is not None else 200

    def to_dict(self):
        return {
            'description': self.msg,
            'status': 'error'
        }

    def __str__(self):
        return self.msg


@db_session
def player_exists(id):
    return Player.exists(id=id)


def clean_kwargs(kwargs):
    for k, v in kwargs.items():
        kwargs[k] = v.strip() if isinstance(v, str) else v


def check_attr_alpha(attr, name):
    error = ""
    attr = attr.strip()
    if not attr:
        error = "Atributo {name} faltante."
    elif not attr.replace(" ", "").isalpha():
        error = "El atributo {name} contiene caracteres no válidos"

    if error:
        raise FbcmError(error.format(name=name))


def check_attr_person_id(id, name='id'):
    error = ""
    id = id.strip()
    if not id:
        error = "Atributo {name} faltante."
    elif not id.isdigit():
        error = "El {name} debe contener sólo números."
    elif len(id) != 10:
        error = "El {name} debe tener 10 dígitos."

    if error:
        raise FbcmError(error.format(name=name))


@db_session
def add_player(**kwargs):
    clean_kwargs(kwargs)
    check_attr_person_id(kwargs.get('id'))
    if player_exists(kwargs.get('id')):
        raise FbcmError('El jugador ya existe.')
    check_attr_alpha(kwargs.get('name'), 'nombre')
    check_attr_alpha(kwargs.get('lastname'), 'apellido')
    try:
        Player(**kwargs)
    except Exception as e:
        print(type(e))
        raise FbcmError(str(e))


@db_session
def get_player(id):
    if not player_exists(id):
        raise FbcmError('El jugador no existe.')
    return Player[id]

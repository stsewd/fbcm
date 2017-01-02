from pony.orm import db_session

from .models import Player, Person


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
def person_exist(id):
    return Person.exists(id=id)


def clean_kwargs(kwargs):
    for k, v in kwargs.items():
        kwargs[k] = v.strip()


def check_attr_alpha(kwargs, k, name):
    error = ""
    if k not in kwargs:
        error = "Atributo {name} faltante."
    elif not kwargs[k].replace(" ", "").strip().isalpha():
        error = "El atributo {name} contiene caracteres no válidos"

    if error:
        raise FbcmError(error.format(name=name))


def check_attr_person_id(kwargs, k='id', name='id'):
    error = ""
    if k not in kwargs:
        error = "Atributo {name} faltante."
    elif not kwargs.get(k, "").strip().isdigit():
        error = "El {name} debe contener sólo números."
    elif len(kwargs.get(k)) != 10:
        error = "El {name} debe tener 10 dígitos."

    if error:
        raise FbcmError(error.format(name=name))


@db_session
def add_player(**kwargs):
    clean_kwargs(kwargs)
    check_attr_person_id(kwargs)
    if person_exist(kwargs.get('id')):
        raise FbcmError('El jugador ya existe.')
    check_attr_alpha(kwargs, 'name', 'nombre')
    check_attr_alpha(kwargs, 'lastname', 'apellido')
    try:
        Player(**kwargs)
    except Exception as e:
        print(type(e))
        raise FbcmError(str(e))

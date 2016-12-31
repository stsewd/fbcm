from pony import orm

from . import db


class Person(db.Entity):
    pid = orm.Required(str)
    name = orm.Required(str)
    lastname = orm.Required(str)

from pony import orm

from . import db


class Person(db.Entity):
    pid = orm.PrimaryKey(str, 10)
    name = orm.Required(str, 40)
    lastname = orm.Required(str, 40)

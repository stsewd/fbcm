from flask import Flask
from pony import orm


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')


db = orm.Database()
orm.sql_debug(app.config['DEBUG'])
db.bind('mysql', host='localhost', user='root', passwd='1234', db='crea una tabla!')

from . import models
db.generate_mapping(create_tables=True)


from . import views


from flask import Flask
from pony import orm


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')


db = orm.Database()
orm.sql_debug(app.config['DEBUG'])
db.bind(
    'mysql',
    host=app.config['DB_HOST'],
    user=app.config['DB_USER'],
    passwd=app.config['DB_PASSWD'],
    db=app.config['DB_NAME']
)


from . import views

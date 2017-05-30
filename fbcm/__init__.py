from flask import Flask


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

from . import views

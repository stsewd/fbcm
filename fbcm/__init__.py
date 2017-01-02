from flask import Flask

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

from . import views
from .models import db

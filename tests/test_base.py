from flask_testing import TestCase
from pony import orm

from fbcm import app
from fbcm.models import db


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

    def setUp(self):
        db.create_tables()
        orm.sql_debug(self.app.config['DEBUG'])

    def tearDown(self):
        db.drop_all_tables(with_all_data=True)

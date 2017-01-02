from flask_testing import TestCase
from pony import orm

from fbcm import app


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

    def setUp(self):
        orm.sql_debug(self.app.config['DEBUG'])

    def tearDown(self):
        from fbcm.models import db
        db.drop_all_tables(with_all_data=True)

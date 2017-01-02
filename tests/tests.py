from flask import url_for

from .test_base import BaseTestCase
import fbcm.services as srv


class PlayerViewsTests(BaseTestCase):
    def test_create_player(self):
        srv.add_player(
            id='1234567891',
            name='Juan',
            lastname='Perez'
        )   
        self.assertTrue(True)

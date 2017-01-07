from pony.orm import db_session
from flask import url_for

from .test_base import BaseTestCase
from fbcm.models import Championship


class ChampionshipsViewsTests(BaseTestCase):
    @db_session
    def assertChampionshipExists(self, name):
        self.assertTrue(Championship.exists(name=name))

    def test_create_championship(self):
        name = "Campeonato de fútbol"
        self.client.post(
            url_for('add_championship'),
            data={
                'name': name
            }
        )

        self.assertChampionshipExists(name)

    def test_create_championship_missig_name(self):
        response = self.client.post(
            url_for('add_team')
        )

        self.assertIn('error', response.json['status'])
        self.assertIn('faltante', response.json['description'])

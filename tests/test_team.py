from pony.orm import db_session
from flask import url_for

from .test_base import BaseTestCase
from fbcm.models import Team


class TeamViewsTests(BaseTestCase):
    @db_session
    def assertTeamExists(self, name):
        self.assertTrue(Team.exists(name=name))

    def test_create_team(self):
        name = "Equipo de fútbol"
        self.client.post(
            url_for('add_team'),
            data={
                'name': name
            }
        )

        self.assertTeamExists(name)

    def test_create_team_missing_name(self):
        response = self.client.post(
            url_for('add_team')
        )

        self.assertIn('error', response.json['status'])
        self.assertIn('faltante', response.json['description'])

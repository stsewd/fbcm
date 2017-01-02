from flask import url_for

from .test_base import BaseTestCase
import fbcm.services as srv


class PlayerViewsTests(BaseTestCase):
    def assertEqualPlayer(self, p, **kwargs):
        self.assertEqual(p.id, kwargs['id'])
        self.assertEqual(p.name, kwargs['name'])
        self.assertEqual(p.lastname, kwargs['lastname'])

    def test_create_player(self):
        id = '1234567890'
        name = 'Juan Alberto'
        lastname = 'Perez'

        self.client.post(
            url_for('add_player'),
            data={
                'id': id,
                'name': name,
                'lastname': lastname
            }
        )

        self.assertEqualPlayer(
            srv.get_player(id),
            id=id,
            name=name,
            lastname=lastname
        )

    def test_create_player_invalid_id(self):
        id = '123456789u'
        name = 'Juan'
        lastname = 'Perez'
        response = self.client.post(
            url_for('add_player'),
            data={
                'id': id,
                'name': name,
                'lastname': lastname
            }
        )
        self.assertIn('error', response.json['status'])
        self.assertIn('id', response.json['description'])

    def test_create_player_invalid_name(self):
        id = '1234567890'
        name = 'Juan 66'
        lastname = 'Perez'
        response = self.client.post(
            url_for('add_player'),
            data={
                'id': id,
                'name': name,
                'lastname': lastname
            }
        )
        self.assertIn('error', response.json['status'])
        self.assertIn('nombre', response.json['description'])

    def test_create_player_missing_value(self):
        id = '1234567890'
        lastname = 'Perez Calle'
        response = self.client.post(
            url_for('add_player'),
            data={
                'id': id,
                'lastname': lastname
            }
        )
        self.assertIn('error', response.json['status'])
        self.assertIn('nombre', response.json['description'])

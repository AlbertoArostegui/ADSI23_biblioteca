from . import BaseTestClass
from unittest.mock import patch
from flask import Flask
from controller.webServer import solicitarAmistad
from controller import LibraryController

class TestAmigos(BaseTestClass): 

    def test_1_get_perfil(self):
        login_response = self.client.post('/login', data={
            'email': 'unai.bermudez@gmail.com',
            'password': '1234' 
        }, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200, 'Login failed')

        response = self.client.get('/perfil?username=admin')
        self.assertEqual(response.status_code, 200)
        
    
    @patch('controller.webServer.library.solicitarAmistad')
    @patch('controller.webServer.library.get_id_by_email')
    @patch('controller.webServer.library.comprobarExisteAmistad')
    def test_2_anadir_amigo(self, mock_comprobarExisteAmistad, mock_get_id_by_email, mock_solicitarAmistad):
        
        mock_comprobarExisteAmistad.return_value = False
        
        mock_get_id_by_email.side_effect = [1, 2] 

        with Flask(__name__).test_request_context('/solicitarAmistad', method='POST',
                                  data={'iduser': 'user1@example.com', 'idamigo': 'user2@example.com'}):
            response = solicitarAmistad()

        mock_solicitarAmistad.assert_called_once_with(1, 2)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/perfil?username=user2@example.com')

    #Make it so it logs in with an account and sends a friend request to another account, then accept that request
    def test_3_aceptar_solicitud(self):
        login_response = self.client.post('/login', data={
            'email': 'unai.bermudez@gmail.com', 
            'password': '1234'
        }, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200, 'Login failed')

        response = self.client.post('/solicitarAmistad', data={
            'iduser': 'unai.bermudez@gmail.com',
            'idamigo': 'admin'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/perfil?username=admin')

        logout_response = self.client.get('/logout')
        self.assertEqual(logout_response.status_code, 302)

        login_response = self.client.post('/login', data={
            'email': 'admin@admin.admin',
            'password': 'admin'
        })

        self.assertEqual(login_response.status_code, 302, 'Login failed')

        response = self.client.post('/aceptarAmistad', data={
            'iduser': 'admin@admin.admin',
            'idamigo': 'unai bermudez'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/perfil?username=admin@admin.admin')
        self.assertEqual(response.status_code, 302)
    
    def test_4_rechazar_solicitud(self):
        # Log in as the first user
        login_response = self.client.post('/login', data={
            'email': 'unai.bermudez@gmail.com',
            'password': 'password'
        })
        self.assertEqual(login_response.status_code, 302, 'Login failed')

        # Send a friend request to the second user
        response = self.client.post('/solicitarAmistad', data={
            'iduser': 'unai.bermudez@gmail.com',
            'idamigo': 'admin'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/perfil?username=admin')

        # Log out
        logout_response = self.client.get('/logout')
        self.assertEqual(logout_response.status_code, 302)

        # Log in as the second user
        login_response = self.client.post('/login', data={
            'email': 'admin@admin.admin',
            'password': 'admin'
        })
        self.assertEqual(login_response.status_code, 302, 'Login failed')

        # Reject the friend request
        response = self.client.post('/rechazarAmistad', data={
            'iduser': 'admin@admin.admin',
            'idamigo': 'unai bermudez'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/perfil?username=admin@admin.admin')

    def test_5_eliminar_amigo(self):
        # Log in as the first user
        login_response = self.client.post('/login', data={
            'email': 'unai.bermudez@gmail.com',
            'password': 'password'
        })
        self.assertEqual(login_response.status_code, 302, 'Login failed')

        # Send a friend request to the second user
        response = self.client.post('/solicitarAmistad', data={
            'iduser': 'unai.bermudez@gmail.com',
            'idamigo': 'admin'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/perfil?username=admin')

        # Log out
        logout_response = self.client.get('/logout')
        self.assertEqual(logout_response.status_code, 302)

        # Log in as the second user
        login_response = self.client.post('/login', data={
            'email': 'admin@admin.admin',
            'password': 'admin'
        })
        self.assertEqual(login_response.status_code, 302, 'Login failed')

        # Accept the friend request
        response = self.client.post('/aceptarAmistad', data={
            'iduser': 'admin@admin.admin',
            'idamigo': 'unai bermudez'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/perfil?username=admin@admin.admin')

        # Remove the friend
        response = self.client.post('/rechazarAmistad', data={
            'iduser': 'admin@admin.admin',
            'idamigo': 'unai bermudez'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/perfil?username=admin@admin.admin')
    
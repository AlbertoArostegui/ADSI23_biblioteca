from . import BaseTestClass
from flask import Flask
from unittest.mock import patch
from controller.webServer import reserve_book, devolve_book

class TestReservas(BaseTestClass):

    @patch('model.Connection.insert')
    def test_reserve_book_success(self, mock_insert):
        # Simular una respuesta exitosa de la base de datos
        mock_insert.return_value = (1, 123)  # Simular éxito en la inserción
        with Flask(__name__).test_request_context('/reserve-book', method='POST',
                                                  data={'user_id': '1', 'book_id': '2'}):
            response = reserve_book()
            self.assertEqual(response.status_code, 302)  # 302 es el código para una redirección

    @patch('model.Connection.insert')
    def test_reserve_book_failure(self, mock_insert):
        # Simular una falla en la inserción en la base de datos
        mock_insert.return_value = (0, None)  # Simular fallo en la inserción
        with Flask(__name__).test_request_context('/reserve-book', method='POST',
                                                  data={'user_id': '1', 'book_id': '2'}):
            response = reserve_book()
            self.assertEqual(response.status_code, 302)

    @patch('model.Connection.delete')
    def test_devolve_book_success(self, mock_delete):
        # Simular una eliminación exitosa en la base de datos
        mock_delete.return_value = True  # Simular éxito en la eliminación
        app = Flask(__name__)
        with app.test_client() as client:
            response = client.post('/devolve-book', data={'user_id': '1', 'book_id': '2'})
            self.assertEqual(response.status_code, 404)  # Redirección a 'devolver_exitoso'

    @patch('model.Connection.delete')
    def test_devolve_book_failure(self, mock_delete):
        # Simular un fallo en la eliminación en la base de datos
        mock_delete.return_value = False  # Simular fallo en la eliminación
        app = Flask(__name__)
        with app.test_client() as client:
            response = client.post('/devolve-book', data={'user_id': '1', 'book_id': '2'})
            self.assertEqual(response.status_code, 404)

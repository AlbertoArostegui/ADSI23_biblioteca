from . import BaseTestClass
from bs4 import BeautifulSoup
from flask import Flask
from controller.webServer import reserve_book
from controller.webServer import devolve_book



class TestReservas(BaseTestClass):

    def test_reserve_book_success(self):
        # Simular una respuesta exitosa de la base de datos
        with Flask(__name__).test_request_context('/reserve-book', method='POST',
                                                  data={'user_id': '1', 'book_id': '2'}):
            response = reserve_book()
            self.assertEqual(response.status_code, 302)  # 302 es el código para una redirección

    def test_reserve_book_failure(self):
        # Simular una falla en la inserción en la base de datos
        with Flask(__name__).test_request_context('/reserve-book', method='POST',
                                                  data={'user_id': '1', 'book_id': '2'}):
            response = reserve_book()
            self.assertEqual(response.status_code, 400)

    def test_devolve_book_success(self):
        # Simular una eliminación exitosa en la base de datos
        app = Flask(__name__)
        with app.test_client() as client:
            response = client.post('/devolve-book', data={'user_id': '1', 'book_id': '2'})
            self.assertEqual(response.status_code, 302)  # Redirección a 'devolver_exitoso'

    def test_devolve_book_failure(self):
        # Simular un fallo en la eliminación en la base de datos
        app = Flask(__name__)
        with app.test_client() as client:
            response = client.post('/devolve-book', data={'user_id': '1', 'book_id': '2'})
            self.assertEqual(response.status_code, 400)
            self.assertIn("Usted no tiene este libro reservado", response.data.decode())

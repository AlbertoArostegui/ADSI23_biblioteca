from . import BaseTestClass
from bs4 import BeautifulSoup
class TestAdmin(BaseTestClass):

    def test_acceso_admin(self):
        res_login = self.client.post('/login', data={
            'email': 'admin@admin.admin',
            'password': 'admin' }, follow_redirects=True)
        self.assertEqual(200, res_login.status_code)
        self.assertIn('token', ''.join(res_login.headers.values()))
        res = self.client.get('/admin')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        admin_boton = page.find('div', class_='btn-group-vertical')
        self.assertIsNotNone(admin_boton)
        self.assertEqual(2, len(admin_boton.find_all('button')))

    def test_crear_usuario(self):
        res_login = self.client.post('/login', data={
            'email': 'admin@admin.admin',
            'password': 'admin'}, follow_redirects=True)
        self.assertEqual(200, res_login.status_code)
        self.assertIn('token', ''.join(res_login.headers.values()))
        res_crear= self.client.post('/gestor_usuarios', data={
            'nombre': 'testman',
            'email': 'testman@test.test',
            'contraseña': '1234',
            'esadmin': 0
            },follow_redirects=True)
        self.assertEqual(200, res_crear.status_code)
        res_existe = self.db.select(f"SELECT * FROM User WHERE name='testman' AND email='testman@test.test' AND admin='0'")
        self.assertNotEqual([], res_existe)
        page = BeautifulSoup(res_crear.data, 'html.parser')
        lista_usuarios = page.find_all('li', class_='list-group-item')
        usuariobuscar = 'testman'

        usuario_encontrado = any(usuariobuscar in str(usuario) for usuario in lista_usuarios)
        self.assertTrue(usuario_encontrado, "NO EXISTE TAL USUARIO")


    def test_delete_user_as_admin(self):
        res_login = self.client.post('/login', data={
            'email': 'admin@admin.admin',
            'password': 'admin'}, follow_redirects=True)
        self.assertEqual(200, res_login.status_code)
        self.assertIn('token', ''.join(res_login.headers.values()))
        res= self.client.post(f'/gestor_usuarios')
        self.assertEqual(200,res.status_code)
        page = BeautifulSoup(res.data, 'html.parser')
        lista_usuarios = page.find_all('li', class_='list-group-item')
        usuariobuscar = 'testman'

        usuario_encontrado = any(usuariobuscar in str(usuario) for usuario in lista_usuarios)
        self.assertTrue(usuario_encontrado,"NO EXISTE TAL USUARIO")
        sqlres = self.db.select(f"SELECT * FROM User WHERE name='testman' AND email='testman@test.test' AND admin='0'")
        res_del = self.client.post('/eliminar_usuario', data={
            'id': sqlres[0][0],
            'nombre': sqlres[0][1],
            'email': sqlres[0][2],
            'contraseña': sqlres[0][3],
            'esadmin': sqlres[0][4] }, follow_redirects=True)
        self.assertEqual(200, res_del.status_code)


    def test_crear_libro(self):
        res_login = self.client.post('/login', data={
            'email': 'admin@admin.admin',
            'password': 'admin'}, follow_redirects=True)
        self.assertEqual(200, res_login.status_code)
        self.assertIn('token', ''.join(res_login.headers.values()))
        res_crear= self.client.post('/gestor_libros', data={
            'titulo': 'test',
            'autor': 'ibai',
            'portada': 'no hay',
            "descripcion": ':('
            },follow_redirects=True)
        self.assertEqual(200, res_crear.status_code)
        res_existe = self.db.select(f"SELECT * FROM Book WHERE title='test' AND description =':('")
        res_existe_autor = self.db.select(f"SELECT * FROM Author WHERE name='ibai'")

        self.assertNotEqual([], res_existe)
        self.assertNotEqual([], res_existe_autor)


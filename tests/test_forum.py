from . import BaseTestClass
from bs4 import BeautifulSoup
class TestForum(BaseTestClass):

    def test_1_forummain(self):
        #se logea
        res = self.login('jhon@gmail.com', '123')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)
		#comprueba que se listan tantos temas como temas en la bd
        res = self.client.get('/forum')
        page = BeautifulSoup(res.data, features="html.parser")
        res = self.db.select(f"SELECT count(*) FROM tema")
        numfilas = res[0][0]
        self.assertEqual(numfilas, len(page.find('div', class_="container p-5 my-5 border").find_all('tr'))) 
        #comprueba que los titulos de los temas mostrados son los titulos de los temas en la bd
        temasenpag = page.find_all("tr")
        i = 0
        while i < numfilas:
            res = self.db.select("SELECT titulo FROM tema LIMIT 1 OFFSET ?", (i,))
            titulo = res[0][0]
            self.assertIn(titulo, temasenpag[i].get_text())
            i = i + 1
        
    def test_2_forummessages(self):
        #se logea
        res = self.login('jhon@gmail.com', '123')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)
		#comprueba que se listan tantos temas como temas en la bd
        res = self.client.get('/forum')
        page = BeautifulSoup(res.data, features="html.parser")
        res = self.db.select(f"SELECT count(*) FROM Tema")
        numtemas = res[0][0]
        i = 0
        while i < numtemas: 
            res2 = self.db.select(f"SELECT titulo FROM Tema WHERE tema_id = ?", (i+1,))
            titulo = res2[0][0]
            print(titulo)
            res3 = self.client.post('/entrartema', data={
                "nomtema":titulo,
	            "idtema": i+1,
	            #"mensajes":mensajes,
                #"foreros":foreros,
	            #"nummensajes" : len(mensajes)
            }, follow_redirects=True)
            self.assertEqual(res3.status_code, 200)
            page = BeautifulSoup(res3.data, features="html.parser")
            res = self.db.select(f"SELECT count(*) FROM TemaMensaje WHERE idtema = ?", (i+1,))
            nummsg = res[0][0]
            mensajes = page.find('div', "container p-5 my-5 border").find_all('tr')
            #print(mensajes)
            #print(len(mensajes))
            self.assertGreater(len(mensajes)+1,nummsg)#el numero de mensajes en la base de datos no es el mismo que el de filas en el tema porque el mensaje al que se responde se almacena en una fila a parte
            i = i + 1

    def test_3_post_message(self):
        #se logea
        res = self.login('jhon@gmail.com', '123')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)
        #cuenta cuantos mensajes tiene el primer tema
        nm = self.db.select(f"SELECT count(*) FROM TemaMensaje WHERE idtema = 1")
        nummsgs = nm[0][0]
        res = self.client.post("/mandandomensajeforo", data={
            "idtema": 1,
            "iduser": 1,
            "nuevomensaje": "hola",
            "nomtema": "Primer Tema"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)#mensaje posteado
        nm = self.db.select(f"SELECT count(*) FROM TemaMensaje WHERE idtema = 1")#cuenta los mensajes de nuevo
        nummsgsahora = nm[0][0]
        self.assertEqual(nummsgs+1,nummsgsahora)#el numero de mensajes ha aumentado en 1






        
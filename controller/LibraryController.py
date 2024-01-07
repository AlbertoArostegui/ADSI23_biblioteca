from model import Connection, Book, User, Review
from model.tools import hash_password


db = Connection()

class LibraryController:
	__instance = None

	def __new__(cls):
		if cls.__instance is None:
			cls.__instance = super(LibraryController, cls).__new__(cls)
			cls.__instance.__initialized = False
		return cls.__instance


	def search_books(self, title="", author="", limit=6, page=0):
		count = db.select("""
				SELECT count() 
				FROM Book b, Author a 
				WHERE b.author=a.id 
					AND b.title LIKE ? 
					AND a.name LIKE ? 
		""", (f"%{title}%", f"%{author}%"))[0][0]
		res = db.select("""
				SELECT b.* 
				FROM Book b, Author a 
				WHERE b.author=a.id 
					AND b.title LIKE ? 
					AND a.name LIKE ? 
				LIMIT ? OFFSET ?
		""", (f"%{title}%", f"%{author}%", limit, limit*page))
		books = [
			Book(b[0],b[1],b[2],b[3],b[4])
			for b in res
		]
		return books, count

	def search_book_by_id(self, book_id):
		res = db.select("""
				SELECT b.* 
				FROM Book b
				WHERE b.id = ?
		""", (book_id,))
		if len(res) > 0:
			book = Book(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
			return book
		else:
			return None

	def add_book(self, titulo, autor, portada, descripcion):
		try:
			id = db.insert("""
					INSERT INTO Author (name)
					VALUES (?)
				""", (autor,))
			db.insert("""
		             INSERT INTO Book (title, author, cover, description)
		             VALUES ( ?, ?, ?, ?)
		        """, (titulo, id[1], portada, descripcion,))

		except Exception as e:
			print(f"Error añadiendo libros: {e}")
	def get_user(self, email, password):
		user = db.select("SELECT * from User WHERE email = ? AND password = ?", (email, hash_password(password)))
		if len(user) > 0:
			return User(user[0][0], user[0][1], user[0][2],None, user[0][4])
		else:
			return None
	def get_all_users(self):
		user = db.select("SELECT * from User")
		if len(user) > 0:
			return user
		else:
			return None
	def get_user_cookies(self, token, time):
		user = db.select("SELECT u.* from User u, Session s WHERE u.id = s.user_id AND s.last_login = ? AND s.session_hash = ?", (time, token))
		if len(user) > 0:
			return User(user[0][0], user[0][1], user[0][2],None,user[0][4])
		else:
			return None

	def add_usuario(self, nombre, email, contraseña, esadmin):
		try:
			hpass = hash_password(contraseña)
			db.insert("""
		             INSERT INTO User (name, email, password, admin)
		             VALUES ( ?, ?, ?, ?)
		        """, (nombre, email, hpass, esadmin,))

		except Exception as e:
			print(f"Error añadiendo libros: {e}")
	def delete_usuario(self, id, nombre, email, contraseña, esadmin):
		try:
			db.delete("""
			          DELETE FROM User
			          WHERE id = ? AND name = ? AND email = ? AND password = ? AND admin = ?
			      """, (id, nombre, email, contraseña, esadmin,))
		except Exception as e:
			print(f"Error borrando usuario: {e}")

		
	def listar_temas(self):
		temas = db.select("SELECT titulo,tema_id FROM Tema")
		#if len(temas) > 0:
		return temas, len(temas)
		#else:
		#	return 0

	def crear_tema(self, titulo, pm, iduser):
		ultimotemaid = db.select("SELECT tema_id FROM Tema WHERE tema_id=(SELECT max(tema_id) FROM Tema)")
		#print(ultimotemaid)
		uti = ultimotemaid[0][0]
		#print(uti)
		idtema = uti + 1
		exito = db.insert("INSERT INTO Tema VALUES (?,?,?)",(idtema,titulo, iduser))
		#db.select("SELECT tema_id FROM Tema WHERE titulo=?", (titulo))
		if exito:
			ultimomensajeid = db.select("SELECT mensaje_id FROM TemaMensaje WHERE mensaje_id=(SELECT max(mensaje_id) FROM TemaMensaje)")
			umi = ultimomensajeid[0][0]
			exito = db.insert("INSERT INTO TemaMensaje VALUES (?,?,?,?, NULL)",(umi+1,pm, iduser, idtema))
			if exito:
				return 1
			else:
				return 0
		else:
			return 0

	def listar_mensajes(self, idtema):
		#mensajes = db.select("SELECT * FROM TemaMensaje WHERE idtema=?", (idtema))
		#mensajes = db.select("SELECT TM1.mensaje_id, TM1.texto, TM1.autor_id, TM1.idtema, TM1.mensaje_resp, TM2.texto AS texto_respuesta FROM TemaMensaje TM1 LEFT JOIN TemaMensaje TM2 ON TM1.mensaje_resp = TM2.mensaje_id WHERE TM1.idtema=?", idtema)
		mensajes = db.select("SELECT TM1.mensaje_id, TM1.texto, TM1.autor_id, TM1.idtema, TM1.mensaje_resp, TM2.texto AS texto_respuesta, U2.name AS nombre_respondido, U1.name AS nombre_autor FROM TemaMensaje TM1 LEFT JOIN User U1 ON TM1.autor_id = U1.id LEFT JOIN TemaMensaje TM2 ON TM1.mensaje_resp = TM2.mensaje_id LEFT JOIN User U2 ON TM2.autor_id = U2.id WHERE TM1.idtema = ?;", idtema)
		foreros = []
		for mensaje in mensajes:
			idmnsj = mensaje[2]
			nuevoforero = db.select("SELECT name FROM User WHERE id=?", (idmnsj,))
			foreros.append(nuevoforero[0][0])
		return mensajes, foreros

	def anadir_mensaje(self, idtema, iduser, texto):
		ultimomensajeid = db.select("SELECT mensaje_id FROM TemaMensaje WHERE mensaje_id=(SELECT max(mensaje_id) FROM TemaMensaje)")
		umi = ultimomensajeid[0][0]
		resultado = db.insert("INSERT INTO TemaMensaje VALUES (?,?,?,?, NULL)",(umi+1,texto,iduser,idtema))
		if resultado:
			return 1
		else:
			return 0

	def responder_mensaje(self, idtema, iduser, texto, idcita):
		ultimomensajeid = db.select("SELECT mensaje_id FROM TemaMensaje WHERE mensaje_id=(SELECT max(mensaje_id) FROM TemaMensaje)")
		umi = ultimomensajeid[0][0]
		resultado = db.insert("INSERT INTO TemaMensaje VALUES (?,?,?,?,?)",(umi+1,texto,iduser,idtema,idcita))
		print("nuevo mensaje respondido")
		print(idcita)
		print(idtema)
		if resultado:
			return 1
		else:
			return 0
		
	def add_usuario(self, nombre, email, contraseña, esadmin):
		try:
			hpass = hash_password(contraseña)
			db.insert("""
		             INSERT INTO User (name, email, password, admin)
		             VALUES ( ?, ?, ?, ?)
		        """, (nombre, email, hpass, esadmin,))

		except Exception as e:
			print(f"Error añadiendo libros: {e}")

	def delete_usuario(self, id, nombre, email, contraseña, esadmin):
		try:
			db.delete("""
			          DELETE FROM User
			          WHERE id = ? AND name = ? AND email = ? AND password = ? AND admin = ?
			      """, (id, nombre, email, contraseña, esadmin,))
		except Exception as e:
			print(f"Error borrando usuario: {e}")


	def save_review(self, book_id, user_email, rating, review_text):
		exito = db.insert("INSERT INTO Reviews (book_id, user_email, rating, review_text) VALUES ( ?, ?, ?, ?)", (book_id, user_email, rating, review_text))
		return 1 if exito else 0

	def get_reviews_by_book_id(self, book_id):
		query = "SELECT * FROM Reviews WHERE book_id = ? ORDER BY date_time DESC"
		reviews = db.select(query, (book_id,))
		return reviews

	def get_review_by_id(self, review_id):
		query = "SELECT * FROM Reviews WHERE id = ?"
		review = db.select(query, (review_id,))
		return review[0] if len(review) > 0 else None
	
	def edit_review(self, review_id, rating, review_text):
		try:
			db.update("""
			          UPDATE Reviews
			          SET rating = ?, review_text = ?
			          WHERE id = ?
			      """, (rating, review_text, review_id,))
		except Exception as e:
			print(f"Error editando review: {e}")

	
	def delete_review(self, review_id):
		try:
			db.delete("""
			          DELETE FROM Reviews
			          WHERE id = ?
			      """, (review_id,))
		except Exception as e:
			print(f"Error borrando review: {e}")


	def get_reviews_by_user(self, user_email):
		query = "SELECT * FROM Reviews WHERE user_email = ? ORDER BY date_time DESC"
		reviews = db.select(query, (user_email,))
		return reviews
	
	def get_reservas_by_user(self, user_id):
		query = "SELECT * FROM reserva WHERE user_id = ?"
		reservas = db.select(query, (user_id,))
		return reservas

from model import Connection, Book, User
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
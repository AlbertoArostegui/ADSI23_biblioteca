import hashlib
import sqlite3
import json

salt = "library"


con = sqlite3.connect("datos.db")
cur = con.cursor()


### Create tables
cur.execute("""
	CREATE TABLE reserva(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		user_id integer,
		book_id integer,
		fecha_inicio date,
		fecha_fin date,
		FOREIGN KEY(user_id) REFERENCES User(id),
		FOREIGN KEY(book_id) REFERENCES Book(id)
	)
""")
cur.execute("""
	CREATE TABLE Author(
		id integer primary key AUTOINCREMENT,
		name varchar(40)
	)
""")

cur.execute("""
	CREATE TABLE Book(
		id integer primary key AUTOINCREMENT,
		title varchar(50),
		author integer,
		cover varchar(50),
		description TEXT,
		FOREIGN KEY(author) REFERENCES Author(id)
	)
""")

cur.execute("""
	CREATE TABLE User(
		id integer primary key AUTOINCREMENT,
		name varchar(20),
		email varchar(30),
		password varchar(32),
		admin boolean
	)
""")

cur.execute("""
	CREATE TABLE Session(
		session_hash varchar(32) primary key,
		user_id integer,
		last_login integer,
		FOREIGN KEY(user_id) REFERENCES User(id)
	)
""")

cur.execute("""
	CREATE TABLE Amistad(
		user1_id integer,
		user2_id integer,
		fecha_inicio DATE NOT NULL,
		fecha_fin DATE,
		FOREIGN KEY(user1) REFERENCES User(id),
		FOREIGN KEY(user2) REFERENCES User(id)
	)
""")


cur.execute("""
	CREATE TABLE Reviews (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		book_id INTEGER,
		user_email TEXT,
		date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		rating INTEGER,
		review_text TEXT
	)
""")
#foro
cur.execute("""
	CREATE TABLE Tema(
		tema_id integer primary key AUTOINCREMENT,
		titulo varchar(32),
		creador_id integer,
		FOREIGN KEY(creador_id) REFERENCES User(id)
	)
""")

cur.execute("""
	CREATE TABLE TemaMensaje(
		mensaje_id integer primary key AUTOINCREMENT,
		texto varchar(64),
		autor_id integer,
		idtema integer NOT NULL REFERENCES Tema(tema_id) ON DELETE CASCADE,
		mensaje_resp integer,
		FOREIGN KEY(mensaje_resp) REFERENCES TemaMensaje(mensaje_id)
		FOREIGN KEY(autor_id) REFERENCES User(id)
	)
""")

cur.execute("""
	INSERT INTO Tema VALUES (1,"Primer Tema",1)
""")

cur.execute("""
	INSERT INTO TemaMensaje VALUES (1,"Primer Tema Mensaje",1, 1, NULL)
""")
### Insert users

with open('usuarios.json', 'r') as f:
	usuarios = json.load(f)['usuarios']

for user in usuarios:
	dataBase_password = user['password'] + salt
	hashed = hashlib.md5(dataBase_password.encode())
	dataBase_password = hashed.hexdigest()
	cur.execute(f"""INSERT INTO User VALUES (NULL, '{user['nombres']}', '{user['email']}', '{dataBase_password}', '{user['admin']}')""")
	con.commit()


#### Insert books
with open('libros.tsv', 'r', encoding="UTF-8") as f:
	libros = [x.split("\t") for x in f.readlines()]

for author, title, cover, description in libros:
	res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	if res.rowcount == -1:
		cur.execute(f"""INSERT INTO Author VALUES (NULL, \"{author}\")""")
		con.commit()
		res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	author_id = res.fetchone()[0]

	cur.execute("INSERT INTO Book VALUES (NULL, ?, ?, ?, ?)",
		            (title, author_id, cover, description.strip()))

	con.commit()


### Insert reviews	
with open('reviews.json', 'r') as f:
	reviews = json.load(f)['reviews']

for review in reviews:
	cur.execute("""INSERT INTO Reviews (book_id, user_email, rating, review_text) VALUES (?, ?, ?, ?)""",
				(review['bookId'], review['user_email'], review['rating'], review['review_text']))
	con.commit()


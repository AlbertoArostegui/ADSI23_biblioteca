from datetime import datetime, timedelta

from model import Connection
from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')


library = LibraryController()


@app.before_request
def get_logged_user():
	if '/css' not in request.path and '/js' not in request.path:
		token = request.cookies.get('token')
		time = request.cookies.get('time')
		if token and time:
			request.user = library.get_user_cookies(token, int(time))
			if request.user:
				request.user.token = token


@app.after_request
def add_cookies(response):
	if 'user' in dir(request) and request.user and request.user.token:
		session = request.user.validate_session(request.user.token)
		response.set_cookie('token', session.hash)
		response.set_cookie('time', str(session.time))
	return response


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/admin')
def admin():
	return render_template('admin.html')
@app.route('/gestor_libros')
def gestor_libros():
	titulo = request.values.get("titulo", "")
	autor = request.values.get("autor", "")
	portada = request.values.get("portada", "")
	descripcion = request.values.get("descripcion", "")
	if titulo != "" and autor != "" and portada != "" and descripcion != "":
		library.add_book(titulo, autor, portada, descripcion)
	return render_template('gestor_libros.html')
@app.route('/gestor_usuarios')
def gestor_usuarios():
	usuarios = library.get_all_users()
	nombre = request.values.get("nombre", "")
	email = request.values.get("email", "")
	contraseña = request.values.get("contraseña", "")
	esadmin = request.values.get("esadmin", "")
	if usuarios != "" and nombre != "" and email != "" and contraseña != "" and esadmin in ["0", "1"]:
		library.add_usuario(nombre,email,contraseña,esadmin)
	return render_template('gestor_usuarios.html', usuarios=usuarios)

@app.route('/catalogue')
def catalogue():
	title = request.values.get("title", "")
	author = request.values.get("author", "")
	page = int(request.values.get("page", 1))
	books, nb_books = library.search_books(title=title, author=author, page=page - 1)
	total_pages = (nb_books // 6) + 1
	return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
	                       total_pages=total_pages, max=max, min=min)


@app.route('/reserva_exitosa')
def reserva_exitosa():
    return render_template('reserva_exitosa.html')


@app.route('/reserve-book', methods=['POST'])
def reserve_book():
    insertar = Connection()
    user_id = request.form.get('user_id')
    book_id = request.form.get('book_id')

    fecha_inicio = datetime.now()
    fecha_fin = fecha_inicio + timedelta(days=60)
    fecha_ini_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

    # Preparar los parámetros para la consulta SQL como una tupla
    p = (user_id, book_id, fecha_ini_str, fecha_fin_str)

    # Pasar la sentencia SQL con marcadores de estilo de SQLite y la tupla de parámetros al método insert
    if insertar.insert("INSERT INTO reserva (user_id, book_id, fecha_inicio, fecha_fin) VALUES (?, ?, ?, ?)", p):
        # Reserva exitosa, redirigir o mostrar un mensaje
        return redirect('reserva_exitosa')
    else:
        # Error en la reserva, manejar adecuadamente
        return "Error en la reserva", 400


@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'user' in dir(request) and request.user and request.user.token:
		return redirect('/')
	email = request.values.get("email", "")
	password = request.values.get("password", "")
	user = library.get_user(email, password)
	if user:
		session = user.new_session()
		resp = redirect("/")
		resp.set_cookie('token', session.hash)
		resp.set_cookie('time', str(session.time))
	else:
		resp = make_response(render_template('login.html'))
	return resp


@app.route('/logout')
def logout():
	path = request.values.get("path", "/")
	resp = redirect(path)
	resp.delete_cookie('token')
	resp.delete_cookie('time')
	if 'user' in dir(request) and request.user and request.user.token:
		request.user.delete_session(request.user.token)
		request.user = None
	return resp

@app.route('/eliminar_usuario')
def eliminar_usuario():
	library.delete_usuario(request.values.get("id", ""), request.values.get("nombre", ""), request.values.get("email", ""), request.values.get("contraseña",""), request.values.get("esadmin",""))
	return redirect('/gestor_usuarios')

@app.route('/forum')
def forum():
	path = request.values.get("path", "/")
	temas, numtemas = library.listar_temas()
	#debug print(temas[0][0])
	return render_template("forum.html", temas=temas, numtemas=numtemas)

@app.route('/creartema')
def creartema():
	path = request.values.get("path", "/")
	return render_template("creartema.html")

@app.route('/creandotema', methods=['POST'])
def creandotema():
	if request.method == 'POST':
		path = request.values.get("path", "/")
		titulo = request.form["nuevotitulo"]
		pm = request.form["primermansaje"]
		userid = request.form["userid"]
		resultado = library.crear_tema(titulo, pm, userid)
		if resultado:
			return render_template("creandotema.html")
		else:
			return render_template("errorcreandotema.html")
	else:
		return render_template("index.html")

@app.route('/entrartema', methods=['POST'])
def entrartema():
	path = request.values.get("path", "/")
	nomtema = request.form["nomtema"]
	idtema = request.form["idtema"]
	mensajes, foreros = library.listar_mensajes(idtema)
	nummensajes = len(mensajes)
	return render_template("entema.html", mensajes=mensajes, nummensajes=nummensajes, foreros=foreros, nomtema=nomtema, idtema=idtema)

@app.route('/nuevomensajeforo' , methods=['POST'])
def nuevomensajeforo():
	path = request.values.get("path", "/")
	idtema = request.form["idtema"]
	nomtema = request.form["nomtema"]
	return render_template("nuevomensajeforo.html", idtema=idtema, nomtema=nomtema)

@app.route('/mandandomensajeforo', methods=['POST'])
def mandandomensajeforo():
	path = request.values.get("path", "/")
	idtema = request.form["idtema"]
	iduser = request.form["iduser"]
	texto = request.form["nuevomensaje"]
	nomtema = request.form["nomtema"]
	resultado = library.anadir_mensaje(idtema,iduser,texto)
	if resultado:
		return render_template("mandandomensajeforo.html", idtema=idtema, nomtema=nomtema)
	else:
		return render_template("errormensajeforo.html")

@app.route('/respondermensajeforo' , methods=['POST'])
def respondermensajeforo():
	path = request.values.get("path", "/")
	idtema = request.form["idtema"]
	nomuser = request.form["nomuser"]
	cita = request.form["cita"]
	idcita = request.form["idcita"]
	nomtema = request.form["nomtema"]
	return render_template("respondermensajeforo.html", idtema=idtema, nomuser=nomuser, cita=cita, idcita=idcita, nomtema=nomtema)

@app.route('/respondiendomensajeforo' , methods=['POST'])
def respondiendomensajeforo():
	path = request.values.get("path", "/")
	idtema = request.form["idtema"]
	texto = request.form["nuevomensaje"]
	iduser = request.form["iduser"]
	idcita = request.form["idcita"] #id del mensaje al que se responde
	nomtema = request.form["nomtema"]
	resultado = library.responder_mensaje(idtema, iduser, texto, idcita)
	if resultado:
		return render_template("respondiendomensajeforo.html", idtema = idtema, nomtema = nomtema)
	else:
		return render_template("errormensajeforo.html")

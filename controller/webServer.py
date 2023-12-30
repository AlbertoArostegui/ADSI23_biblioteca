from datetime import datetime, timedelta
from model.Connection import Connection

from controller.LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect, url_for

import sqlite3

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

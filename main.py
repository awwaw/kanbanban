from flask import render_template, Flask, request, url_for, make_response,\
    session, redirect, abort
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, email_validator
import sqlalchemy
import requests

from data.Forms import LoginForm, RegisterForm, NewBoardForm

#TODO: Пофиксить говно с вылетом при добавлении работы

from data import db_session, User, Task, __all_models, Board

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexliceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User.User).get(user_id)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Регистрация", form=form, message="Пароли не совпадают")
        session =  db_session.create_session()
        if session.query(User.User).filter(User.User.email == form.email.data).first():
            return render_template("register.html", title="Регистрация", form=form,
                                   message="Пользователь с таким адресом электронной почты уже существует")
        if session.query(User.User).filter(User.User.name == form.name.data).first():
            return render_template("register.html", title="Регистрация", form=form,
                                   message="Пользователь с таким именем уже существует")
        user = User.User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title="Регистрация", form=form, message="1")


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User.User).filter(User.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template("login.html",
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template("login.html", title="Авторизация", form=form, message="1")


@app.route('/')
def mainPage():
    if current_user.is_authenticated:
        session = db_session.create_session()
        boards = session.query(Board.Board)
        return render_template('index.html', boards=boards)
    else:
        return render_template("mainPage.html", title="Kanbanban")


@app.route('/new_board', methods=['POST', 'GET'])
@login_required
def new_board():
    if current_user.is_authenticated:
        form = NewBoardForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            if session.query(Board.Board).filter(Board.Board.title == form.title.data).first():
                return render_template('new_board.html', message="Доска с таким именем уже существует", form=form)
            board = Board.Board(
                title=form.title.data,
                isPrivate=form.isPrivate.data,
                user_id=current_user.id
            )
            user = session.query(User.User).filter(User.User.id == current_user.id).first()
            user.board.append(board)
            session.merge(user)
            # session.add(board)
            session.commit()
            return redirect('/') #TODO: Сделать перенаправление на страницу доски
        return render_template("new_board.html", title="Новая доска", form=form)
    return redirect('/login')


if __name__ == '__main__':
    db_session.global_init("db/blogs.sqlite")
    app.run(port=8080, host='127.0.0.1')
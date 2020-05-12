from flask import render_template, Flask, request, url_for, make_response,\
    session, redirect, abort
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, email_validator
import sqlalchemy
import requests
import os
from flask_ngrok import run_with_ngrok

from sqlalchemy import or_

from data.Forms import LoginForm, RegisterForm, NewBoardForm, NewTaskForm

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


@app.route('/delete_board/<id>', methods=['POST', 'GET'])
@login_required
def delete_board(id):
    session = db_session.create_session()
    board = session.query(Board.Board).filter(Board.Board.id == int(id),
                                              Board.Board.user == current_user).first()
    if board:
        session.delete(board)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/edit_board/<id>', methods=['POST', 'GET'])
@login_required
def edit_board(id):
    form = NewBoardForm()
    if request.method == 'GET':
        session = db_session.create_session()
        board = session.query(Board.Board).filter(Board.Board.id == int(id)).first()
        if board:
            form.title.data = board.title
            #TODO: Если будут добавлены еще свойства доски, добавить их сюда
        else:
            abort(404)

    if form.validate_on_submit():
        session = db_session.create_session()
        board = session.query(Board.Board).filter(Board.Board.id == int(id),
                                                  Board.Board.user == current_user).first()
        if board:
            board.title = form.title.data
            session.commit()
            return redirect('/')
        else:
            abort(404)

    return render_template('new_board.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def mainPage():
    if current_user.is_authenticated:
        session = db_session.create_session()
        boards = session.query(Board.Board).filter(or_(Board.Board.user_id == current_user.id,
                                                   Board.Board.workers.contains(str(current_user.id))))[::-1]
        for board in boards:
            print(board.user.name)
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
            if session.query(Board.Board).filter(Board.Board.title == form.title.data,
                                                 Board.Board.user == current_user).first():
                return render_template('new_board.html', message="Доска с таким именем уже существует", form=form)
            user = session.query(User.User).filter(User.User.id == current_user.id).first()
            board = Board.Board(
                title=form.title.data,
                isPrivate=form.isPrivate.data,
                user_id=user.id,
                workers=str(current_user.id) + ',',
                author=user.name,
                user=user,
                # tasks="#,"
            )
            # board.workers.append(str(current_user.id))  # TODO: Не забыть добавлять ЗАПЯТУЮ при приглашениях

            user.board.insert(0, board)
            session.merge(user)
            id = board.id
            # session.add(board)
            session.commit()
            return redirect('/board/' + str(id)) #TODO: Сделать перенаправление на страницу доски
        return render_template("new_board.html", title="Новая доска", form=form)
    return redirect('/login')


@app.route('/board')
def b():
    return redirect('/')


@app.route('/board/<id>', methods=['POST', 'GET'])
@login_required
def board(id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        # tasks = session.query(Task.Task).filter(Task.Task.board == int(id))
        #TODO (возможно): переделать на tasks = cur_board.tasks.split(',')
        cur_board = session.query(Board.Board).filter(Board.Board.id == int(id)).first()
        if cur_board:
            members = str(cur_board.workers).split(',')
        else:
            return abort(404)
        tasks = cur_board.tasks
        TASKS = []
        for TASK in tasks:
            TASKS.append(TASK)
        MEMBERS = []
        for id in members:
            if id.isdigit():
                MEMBER = session.query(User.User).filter(User.User.id == int(id)).first()
                if MEMBER:
                    MEMBERS.append(MEMBER)
        if cur_board.isPrivate and str(current_user.id) not in members:
            return render_template('oops.html')
        session.commit()
        return render_template('board.html', tasks=TASKS, members=MEMBERS, board=cur_board)
    return redirect('/login')


@app.route('/add_task/<int:_id>', methods=['POST', 'GET'])
@login_required
def add_task(_id):
    if current_user.is_authenticated:
        form = NewTaskForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            board = session.query(Board.Board).filter(Board.Board.id == _id).first()
            TASKS = board.tasks
            if len(TASKS) == 0:
                taskId = 1
            else:
                taskId = int(TASKS[-1].id) + 1

            task = Task.Task(
                # id=taskId,
                title=form.title.data,
                content=form.content.data,
                author=current_user.name,
                user_id=current_user.id,
                # board=_id
            )
            # taskId = task.id
            # print(taskId)
            # board.tasks = board.tasks + str(task.id) + ','
            board.tasks.insert(0, task)
            print(board.tasks)
            session.merge(board)
            session.commit()
            return redirect('/board/' + str(_id))
        return render_template('new_task.html', form=form)
    return redirect('/login')


@app.route('/join/<int:id>', methods=['POST', 'GET'])
@login_required
def join(id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        board = session.query(Board.Board).filter(Board.Board.id == id).first()
        if board:
            board.workers = board.workers + str(current_user.id) + ','
            user = session.query(User.User).filter(User.User.id == current_user.id).first()
            user.board.insert(0, board)
            session.merge(user)
            session.commit()
            return redirect('/board/' + str(id))
        else:
            abort(404)
    else:
        return redirect('/login')



if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')
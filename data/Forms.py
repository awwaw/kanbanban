from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, email_validator


class RegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    password_again = PasswordField(validators=[DataRequired()])
    reg = SubmitField("reg")


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    login = SubmitField("login")


class NewBoardForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    isPrivate = BooleanField("Приватная?")
    create = SubmitField("Создать")


class NewTaskForm(FlaskForm):
    title = StringField("Заголовок")
    content = TextAreaField("Текст записи", validators=[DataRequired()])
    add = SubmitField("Добавить")
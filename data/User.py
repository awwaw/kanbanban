import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug import security
from sqlalchemy import orm

class User(SqlAlchemyBase, UserMixin):

    __tablename__ = 'users'

    def set_password(self, password):
        self.hashed_password = security.generate_password_hash(password)

    def check_password(self, password):
        return security.check_password_hash(self.hashed_password, password)

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    task = orm.relation("Task", back_populates='user')
    board = orm.relation("Board", back_populates='user')
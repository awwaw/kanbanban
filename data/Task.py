import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    collaborators = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    TeamLeader = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    author = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    board = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("board.id"))
    files = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')
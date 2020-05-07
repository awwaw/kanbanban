import datetime
import sqlalchemy
from sqlalchemy import orm, PrimaryKeyConstraint, ForeignKeyConstraint

from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'


    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    author = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    board = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("boards.id"))
    files = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # user = orm.relation('User')
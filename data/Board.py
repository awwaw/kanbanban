import datetime
import sqlalchemy
from sqlalchemy import orm, PrimaryKeyConstraint

from .db_session import SqlAlchemyBase


class Board(SqlAlchemyBase):
    __tablename__ = 'boards'

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True,
                           primary_key=True)
    author = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    workers = sqlalchemy.Column(sqlalchemy.String)
    tasks = sqlalchemy.Column(sqlalchemy.String)
    isPrivate = sqlalchemy.Column(sqlalchemy.Boolean)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    def getWorkers(self):
        return list(self.workers.split(','))

    def getTasks(self):
        return list(self.tasks.split(','))

    def deleteWorker(self, id):
        workers = self.getWorkers()
        pos = workers.index(id)
        workers[pos] = ''
        self.workers = ','.join(workers)

    def deleteTask(self, id):
        tasks = self.getWorkers()
        pos = tasks.index(id)
        tasks[pos] = ''
        self.tasks = ','.join(tasks)
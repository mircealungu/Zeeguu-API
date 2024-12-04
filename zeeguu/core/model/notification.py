import sqlalchemy
from zeeguu.api.utils.abort_handling import make_error
import zeeguu.core
from sqlalchemy import Column, Integer, String

from zeeguu.core.model import db
from zeeguu.core.model.language import Language


class Notification(db.Model):
    """
    A Notification reflects the diferent types of notifications
    that the system is able to output.

    """

    __table_args__ = {"mysql_collate": "utf8_bin"}

    id = Column(Integer, primary_key=True)
    type = db.Column(db.String)

    # Should match the ids in the Database
    # this class is dined to make it easier to
    # quickly accss the code.

    EXERCISE_AVAILABLE = 1
    NEW_ARTICLE_AVAILABLE = 2
    DAILY_LOGIN = 3

    def __init__(self):
        self.type = type

    def __repr__(self):
        return f"<Notification: {self.id} Type: {self.type}>"

    @classmethod
    def find(cls, type):
        try:
            notification = cls.query.filter(cls.type == type).one()
            return notification
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    @classmethod
    def find_by_id(cls, i):
        try:
            notification = cls.query.filter(cls.id == i).one()
            return notification
        except Exception as e:
            from sentry_sdk import capture_exception

            capture_exception(e)
            return None
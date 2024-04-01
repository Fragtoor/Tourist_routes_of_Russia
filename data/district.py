from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin


class District(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'district'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    trips = sqlalchemy.Column(sqlalchemy.String)
    image = sqlalchemy.Column(sqlalchemy.String)

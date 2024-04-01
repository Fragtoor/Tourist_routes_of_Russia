from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin


class Trip(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'trip'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    district = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('district.id'))
    settlements = sqlalchemy.Column(sqlalchemy.String)
    des_settlements = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    # Ссылка на static api yandex
    route = sqlalchemy.Column(sqlalchemy.String)
    fame = sqlalchemy.Column(sqlalchemy.String)
    image = sqlalchemy.Column(sqlalchemy.String)

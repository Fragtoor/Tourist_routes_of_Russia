from .db_session import SqlAlchemyBase
import sqlalchemy


class Reviews(SqlAlchemyBase):
    __tablename__ = 'reviews'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    like = sqlalchemy.Column(sqlalchemy.String)
    trip_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('trip.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

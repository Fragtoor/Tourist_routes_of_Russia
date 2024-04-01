from .db_session import SqlAlchemyBase
import sqlalchemy


class DesSettlements(SqlAlchemyBase):
    __tablename__ = 'des_settlements'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    description = sqlalchemy.Column(sqlalchemy.String)
    image = sqlalchemy.Column(sqlalchemy.String)

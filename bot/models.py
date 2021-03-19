from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()

def db_connect():
    return create_engine('sqlite:///database.db')

def create_items_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Item(DeclarativeBase):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    stock_status = Column('stock_status', Integer, nullable=False)
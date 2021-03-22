from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

DeclarativeBase = declarative_base()

load_dotenv()
TOKEN = os.getenv('TOKEN')
DATABASE_URL = os.getenv('POSTGRES_URL')

def db_connect():
    return create_engine(DATABASE_URL)

def create_items_table(engine):
    DeclarativeBase.metadata.create_all(engine)

engine = db_connect()
create_items_table(engine)
Session = sessionmaker(bind=engine)
db = Session()

class Item(DeclarativeBase):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    stock_status = Column('stock_status', Integer, nullable=False)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_url = 'sqlite:///todo.database.db'

engine = create_engine(db_url)

session = sessionmaker(bind=engine)
Base = declarative_base()

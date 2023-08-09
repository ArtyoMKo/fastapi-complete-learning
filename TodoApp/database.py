"""
Going to be used for link FastAPI application with our sqlite database
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

# By default, sqlalchemy engine using 1 thread. With this parameter we are saying `do not
# check same thread because fastapi could use multiple threads
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

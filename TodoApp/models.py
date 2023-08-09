from sqlalchemy import Column, Integer, String, Boolean
from TodoApp.database import Base


class Todos(Base):
    __tablename__ = (
        "todos"  # For help sqlalchemy to know what is the name of table later on
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)

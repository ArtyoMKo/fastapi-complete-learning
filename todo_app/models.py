from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from todo_app.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)

    def update(self, **kwargs):
        for field, value in kwargs.items():
            if value is not None:
                setattr(self, field, value)


class Todos(Base):
    __tablename__ = (
        "todos"  # For help sqlalchemy to know what is the name of table later on
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    def update(self, **kwargs):
        for field, value in kwargs.items():
            if value is not None:
                setattr(self, field, value)

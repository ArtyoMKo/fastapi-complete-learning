from sqlalchemy import Column, Integer, String, Boolean
from todo_app.database import Base


class Todos(Base):
    __tablename__ = (
        "todos"  # For help sqlalchemy to know what is the name of table later on
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    complete = Column(Boolean, default=False)

    # def update(self, title, description, priority, complete):
    #     self.title = title
    #     self.description = description
    #     self.priority = priority
    #     self.complete = complete

    def update(self, **kwargs):
        for field, value in kwargs.items():
            if value is not None:
                setattr(self, field, value)

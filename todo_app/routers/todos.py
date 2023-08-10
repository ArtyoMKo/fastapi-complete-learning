from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status, Path
from todo_app.models import Todos
from todo_app.database import SessionLocal
from todo_app.exceptions import TODONotFoundException

router = APIRouter()


def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


DbDependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=330)
    priority: int = Field(gt=0, lt=7)
    complete: bool = Field(default=False)
    owner_id: int = Field(gt=0)


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    complete: Optional[bool] = None
    owner_id: Optional[int] = None


@router.get("/")
async def read_all(database: DbDependency):
    return database.query(Todos).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(database: DbDependency, todo_id: int = Path(gt=0)):
    todo_element = database.query(Todos).filter(Todos.id == todo_id).first()
    if todo_element is None:
        raise TODONotFoundException
    return todo_element


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(database: DbDependency, todo_request: TodoRequest):
    new_todo_element = Todos(**todo_request.model_dump())

    database.add(new_todo_element)
    database.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    database: DbDependency, todo_request: TodoUpdate, todo_id: int = Path(gt=0)
):
    updatable_todo = database.query(Todos).filter(Todos.id == todo_id).first()
    if not updatable_todo:
        raise TODONotFoundException

    updatable_todo.update(**todo_request.model_dump(exclude_unset=True))

    database.add(updatable_todo)
    database.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(database: DbDependency, todo_id: int = Path(gt=0)):
    deletable_todo = database.query(Todos).filter(Todos.id == todo_id).first()
    if not deletable_todo:
        raise TODONotFoundException
    database.delete(deletable_todo)
    database.commit()

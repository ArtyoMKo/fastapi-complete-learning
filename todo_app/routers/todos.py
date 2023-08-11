from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status, Path
from todo_app.models import Todos
from todo_app.database import get_db
from todo_app.exceptions import TODONotFoundException
from todo_app.routers.auth import get_current_user

router = APIRouter(prefix="/todo", tags=["todo"])

DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=330)
    priority: int = Field(gt=0, lt=7)
    complete: bool = Field(default=False)


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    complete: Optional[bool] = None


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: UserDependency, database: DbDependency):
    return database.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(
    user: UserDependency, database: DbDependency, todo_id: int = Path(gt=0)
):
    todo_element = (
        database.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_element is None:
        raise TODONotFoundException
    return todo_element


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: UserDependency, database: DbDependency, todo_request: TodoRequest
):
    new_todo_element = Todos(**todo_request.model_dump(), owner_id=user.get("id"))

    database.add(new_todo_element)
    database.commit()


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: UserDependency,
    database: DbDependency,
    todo_request: TodoUpdate,
    todo_id: int = Path(gt=0),
):
    updatable_todo = (
        database.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if not updatable_todo:
        raise TODONotFoundException

    updatable_todo.update(**todo_request.model_dump(exclude_unset=True))

    database.add(updatable_todo)
    database.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: UserDependency, database: DbDependency, todo_id: int = Path(gt=0)
):
    deletable_todo = (
        database.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if not deletable_todo:
        raise TODONotFoundException
    database.delete(deletable_todo)
    database.commit()

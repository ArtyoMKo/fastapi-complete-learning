from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Path
from todo_app.models import Todos, Users
from todo_app.database import get_db
from todo_app.exceptions import TODONotFoundException, AuthenticationFailed
from todo_app.routers.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all_todos(user: UserDependency, database: DbDependency):
    if user is None or user.get("user_role") != "admin":
        raise AuthenticationFailed
    return database.query(Todos).all()


@router.get("/user", status_code=status.HTTP_200_OK)
async def read_all_users(user: UserDependency, database: DbDependency):
    if user is None or user.get("user_role") != "admin":
        raise AuthenticationFailed
    return database.query(Users).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: UserDependency, database: DbDependency, todo_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise AuthenticationFailed
    todo = database.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise TODONotFoundException
    database.delete(todo)
    database.commit()

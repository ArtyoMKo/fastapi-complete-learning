from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status, Path
from todo_app.models import Todos
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
async def read_all(user: UserDependency, database: DbDependency):
    if user is None or user.get("user_role") != "admin":
        raise AuthenticationFailed
    return database.query(Todos).all()

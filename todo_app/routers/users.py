from typing import Annotated, Optional, Union
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, status
from todo_app.models import Todos, Users
from todo_app.database import get_db
from todo_app.exceptions import AuthenticationFailed, UserNotFoundException
from todo_app.routers.auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(get_current_user)]


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    new_password: Optional[str] = None
    password: str


def verify_password(hashed_password: Union[str, bytes], password: Union[str, bytes]) -> bool:
    if bcrypt_context.verify(password, hashed_password):
        return True
    return False


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: UserDependency, database: DbDependency):
    user_info = database.query(Users).filter(Users.username == user.get("username")).first()
    if not user_info:
        raise UserNotFoundException
    return user_info


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
        user: UserDependency,
        database: DbDependency,
        user_request: UserUpdate
):
    updatable_user = (
        database.query(Users)
        .filter(Todos.id == user.get('id'))
        .first()
    )
    if not updatable_user:
        raise UserNotFoundException
    if not verify_password(
            updatable_user.hashed_password.encode('utf-8'),
            user_request.password.encode('utf-8')
    ):
        raise AuthenticationFailed
    user_updates = user_request.model_dump(exclude_unset=True)
    if user_updates.get('new_password'):
        user_updates.update(
            {'hashed_password': bcrypt_context.hash(user_updates.pop('new_password'))}
        )
    updatable_user.update(**user_updates)

    database.add(updatable_user)
    database.commit()

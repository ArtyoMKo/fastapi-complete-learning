from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from todo_app.models import Users
from todo_app.database import SessionLocal
from todo_app.exceptions import AuthenticationFailed

router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


DbDependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, database) -> bool:
    user = database.query(Users).filter(Users.username == username).first()
    if user and bcrypt_context.verify(password, user.hashed_password):
        return True
    return False


@router.post("/auth", status_code=status.HTTP_201_CREATED)
def create_user(database: DbDependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True,
    )

    database.add(create_user_model)
    database.commit()


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], database: DbDependency
):
    user_authenticated: bool = authenticate_user(
        form_data.username, form_data.password, database
    )
    if not user_authenticated:
        raise AuthenticationFailed
    return "Successful Authentication"

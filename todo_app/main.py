from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, status, Path
from starlette.responses import JSONResponse
from starlette.requests import Request
from todo_app import models
from todo_app.models import Todos
from todo_app.database import engine, SessionLocal
from todo_app.exceptions import TODONotFoundException

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"Oops!. Internal server error with message {exc}"},
    )


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


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    complete: Optional[bool] = None


@app.get("/")
async def read_all(database: DbDependency):
    return database.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(database: DbDependency, todo_id: int = Path(gt=0)):
    todo_element = database.query(Todos).filter(Todos.id == todo_id).first()
    if todo_element is None:
        raise TODONotFoundException
    return todo_element


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(database: DbDependency, todo_request: TodoRequest):
    new_todo_element = Todos(**todo_request.model_dump())

    database.add(new_todo_element)
    database.commit()


@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    database: DbDependency, todo_request: TodoUpdate, todo_id: int = Path(gt=0)
):
    updatable_todo = database.query(Todos).filter(Todos.id == todo_id).first()
    if not updatable_todo:
        raise TODONotFoundException

    updatable_todo.update(**todo_request.model_dump(exclude_unset=True))

    database.add(updatable_todo)
    database.commit()


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(database: DbDependency, todo_id: int = Path(gt=0)):
    deletable_todo = database.query(Todos).filter(Todos.id == todo_id).first()
    if not deletable_todo:
        raise TODONotFoundException
    database.delete(deletable_todo)
    database.commit()

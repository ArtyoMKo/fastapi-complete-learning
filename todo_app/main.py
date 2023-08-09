from fastapi import FastAPI
from todo_app import models
from todo_app.database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.requests import Request
from todo_app import models
from todo_app.database import engine
from todo_app.routers import auth, todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todos.router)


@app.exception_handler(Exception)
async def exception_handler(
    request: Request, exc: Exception
):  # pylint: disable=unused-argument
    return JSONResponse(
        status_code=500,
        content={"message": f"Oops!. Internal server error with message {exc}"},
    )

from fastapi import FastAPI, Depends
from routers import users, tasks
from database import Base, engine

from contextlib import asynccontextmanager
from fastapi.exception_handlers import(http_exception_handler, request_validation_exception_handler)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)



app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request,
    exception: StarletteHTTPException
):
    return await http_exception_handler(request, exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request,
    exception: RequestValidationError
):
    return await request_validation_exception_handler(request, exception)
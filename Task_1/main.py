from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import Base, engine
from routers import students, courses, enrollments


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Student Record Management API",
    description="CodSoft Internship Task 1 - Asynchronous REST API for managing Students, Courses, and Enrollments.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(enrollments.router, prefix="/api/enrollments", tags=["Enrollments"])


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request, exception: StarletteHTTPException):
    return await http_exception_handler(request, exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exception: RequestValidationError):
    return await request_validation_exception_handler(request, exception)

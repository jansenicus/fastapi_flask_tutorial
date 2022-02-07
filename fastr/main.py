from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from fastr.api import auth, blog, hello
from fastr.db import models
from fastr.db.database import engine
from fastr.lib.config import Settings


# create the database tables
models.Base.metadata.create_all(bind=engine)

API = FastAPI()

settings = Settings()
API.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
API.mount("/static", StaticFiles(directory="fastr/res"), name="static")
API.include_router(hello.api)
API.include_router(auth.api, prefix="/auth", tags=["auth"])
API.include_router(blog.api, tags=["blog"])


@API.exception_handler(blog.RequiresLoginException)
def exception_handler(request: Request, exc: blog.RequiresLoginException) -> Response:
    """
    Redirect to login screen if someone tries to access a view that requires login.

    Workaround suggested in a GitHub comment here:
    https://github.com/tiangolo/fastapi/issues/1039#issuecomment-591661667
    """
    return RedirectResponse(url="/auth/login", status_code=302)
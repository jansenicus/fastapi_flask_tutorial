from . import *

@api.get("/hello", response_class=HTMLResponse)
async def hello() -> str:
    """A simple page that says hello"""
    return "Hello, World!"
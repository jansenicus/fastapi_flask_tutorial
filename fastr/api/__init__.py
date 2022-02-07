from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastr.db import crud, schemas, models
from fastr.db.database import get_db


html = Jinja2Templates(directory=str("fastr/html"))
api = APIRouter()

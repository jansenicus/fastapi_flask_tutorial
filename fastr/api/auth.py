from . import *
from passlib.context import CryptContext
from fastr.lib.utils import flash

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@api.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    """Display the user registration page"""
    return html.TemplateResponse("auth/register.html", {"request": request})


@api.post("/register", response_class=HTMLResponse)
def register_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Validates that the username is not already taken. Hashes the password for security.

    Note: username and password are specified as required fields, so FastAPI's input
    validation will make sure they are populated. No need for an explicit check that
    they are not None or "".
    """
    error = None

    if crud.get_user_by_username(db, username):
        error = f"User {username} is already registered."

    if error is None:
        # Success -- add user to database and redirect to login screen
        hashed_password = get_password_hash(password)
        user = schemas.UserCreate(username=username, hashed_password=hashed_password)
        crud.create_user(db, user)
        return RedirectResponse("/auth/login", status_code=302)
    else:
        # Error -- redirect back to register page and flash the error
        flash(request, error)
        return RedirectResponse("/auth/register", status_code=302)


@api.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Display the login page"""
    return html.TemplateResponse("auth/login.html", {"request": request})


@api.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Log in a registered user by adding the user id to the session."""
    error = None

    user = crud.get_user_by_username(db, username)

    if user is None:
        error = "Incorrect username."
    elif not verify_password(password, user.hashed_password):
        error = "Incorrect password."

    if error is None:
        # Success -- populate user_id in the session and go to index
        clear_session(request)
        logged_in_user = schemas.LoggedInUser(id=user.id, username=user.username)
        request.session["user"] = logged_in_user.dict()
        return RedirectResponse("/", status_code=302)
    else:
        # Error -- redirect back to login page
        flash(request, error)
        return RedirectResponse("/auth/login", status_code=302)


@api.get("/logout", response_class=HTMLResponse)
def logout_page(request: Request):
    """Clear the current session, including the stored user id."""
    clear_session(request)
    return RedirectResponse("/", status_code=302)


def clear_session(request: Request):
    """Remove all keys from request.session"""
    keys = list(request.session.keys())
    for k in keys:
        request.session.pop(k)

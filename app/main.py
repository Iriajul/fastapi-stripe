from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from . import models, database, users, payments, auth

import os

app = FastAPI(
    title="Auth & Subscription API",
    description="API for user authentication, subscription, and Stripe payment integration",
    version="1.0.0",
)

# -----------------------
# Middleware Configuration
# -----------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="your_session_secret_here")

# -----------------------
# Jinja2 Templates
# -----------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# -----------------------
# Database Initialization
# -----------------------

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=database.engine)

# -----------------------
# API Routers
# -----------------------

app.include_router(users.router)
app.include_router(payments.router)
app.include_router(auth.router)

# -----------------------
# HTML Frontend Routes
# -----------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
def signup_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db),
):
    existing_user = db.query(models.UserProfile).filter_by(username=username).first()
    if existing_user:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "Username already exists."
        })

    hashed = auth.get_password_hash(password)
    user = models.UserProfile(username=username, hashed_password=hashed)
    db.add(user)
    db.commit()
    return RedirectResponse("/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db),
):
    user = db.query(models.UserProfile).filter_by(username=username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid credentials"
        })

    access_token = auth.create_access_token(data={"sub": user.username})
    refresh_token = auth.create_refresh_token(data={"sub": user.username})

    # ✅ FIX: Reattach the user object to the session before commit
    user.refresh_token = refresh_token
    db.add(user)               # ✅ REQUIRED
    db.commit()
    db.refresh(user)           # optional but helpful

    response = RedirectResponse("/profile", status_code=302)
    response.set_cookie("access_token", access_token, httponly=False, samesite="Lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax")

    request.session["user"] = user.username
    return response



@app.get("/profile", response_class=HTMLResponse)
def view_profile(request: Request, db: Session = Depends(database.get_db)):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=302)

    user = db.query(models.UserProfile).filter_by(username=username).first()
    if not user:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


@app.get("/logout")
def logout(
    request: Request,
    db: Session = Depends(database.get_db)
):
    username = request.session.get("user")
    if username:
        # Clear refresh token from database
        user = db.query(models.UserProfile).filter_by(username=username).first()
        if user:
            user.refresh_token = None
            db.commit()

    # Clear session and cookies
    request.session.clear()
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@app.get("/success", response_class=HTMLResponse)
def success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})


@app.get("/cancel", response_class=HTMLResponse)
def cancel(request: Request):
    return templates.TemplateResponse("cancel.html", {"request": request})

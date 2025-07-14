from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, database, config

router = APIRouter(prefix="/api/authentication", tags=["authentication"])

# -----------------------
# Config & Secrets
# -----------------------
SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = config.REFRESH_TOKEN_EXPIRE_DAYS

# -----------------------
# Security & OAuth2
# -----------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/authentication/login/")

# -----------------------
# Utility Functions
# -----------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = database.SessionLocal()
    print("[DB] Connected to DB session")
    try:
        yield db
    finally:
        db.close()

# -----------------------
# Protected Route Auth
# -----------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.UserProfile).filter(models.UserProfile.username == username).first()
    if not user:
        raise credentials_exception
    return user

# -----------------------
# Authentication Logic
# -----------------------
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.UserProfile).filter(models.UserProfile.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

@router.post("/login/", name="api_login_user")
def login_user_api(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    db_user = db.query(models.UserProfile).filter(models.UserProfile.id == user.id).first()
    if db_user:
        db_user.refresh_token = refresh_token
        db.commit()
        db.refresh(db_user)
        print(f"[LOGIN] Saved refresh_token for {db_user.username}")
    else:
        print("[LOGIN] User not found in DB!")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/token/refresh/")
def refresh_token_endpoint(
    refresh_token: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(models.UserProfile).filter(models.UserProfile.username == username).first()

        print(f"[REFRESH] DB token: {user.refresh_token if user else 'User not found'}")
        print(f"[REFRESH] Sent token: {refresh_token}")

        if not user or user.refresh_token != refresh_token:
            print(f"[REFRESH] Token mismatch for {username}")
            raise HTTPException(status_code=401, detail="Token mismatch or user not found")

        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout/")
def logout_user(
    current_user: models.UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.refresh_token = None
    db.commit()
    return {"message": "Logged out successfully"}

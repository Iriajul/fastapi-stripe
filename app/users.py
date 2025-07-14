from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, auth

router = APIRouter(prefix="/api/authentication", tags=["authentication"])

@router.post("/signup/", response_model=schemas.UserProfileOut, status_code=status.HTTP_201_CREATED)
async def signup(user: schemas.UserProfileCreate, db: Session = Depends(auth.get_db)) -> models.UserProfile:
    db_user = db.query(models.UserProfile).filter(models.UserProfile.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.UserProfile(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login/", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(auth.get_db)
) -> dict:
    username = form_data.username
    password = form_data.password

    db_user = db.query(models.UserProfile).filter(models.UserProfile.username == username).first()
    if not db_user or not auth.verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    access_token = auth.create_access_token(data={"sub": db_user.username})
    refresh_token = auth.create_refresh_token(data={"sub": db_user.username})

    # ✅ Save refresh token to DB
    db_user.refresh_token = refresh_token
    #db.add(db_user)  # Ensure changes are tracked
    db.commit()      # Persist to database
    db.refresh(db_user)  # Optional but good practice

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/get_user_profile/", response_model=schemas.UserProfileOut)
async def get_user_profile(current_user: models.UserProfile = Depends(auth.get_current_user)) -> models.UserProfile:
    return current_user

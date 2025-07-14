from pydantic import BaseModel, EmailStr

class UserProfileCreate(BaseModel):
    # Assuming username is an email address
    username: EmailStr
    password: str

class UserProfileOut(BaseModel):
    username: EmailStr
    is_subscribed: bool

    class Config:
         from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

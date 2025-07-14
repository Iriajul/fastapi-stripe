from sqlalchemy import Boolean, Column, Integer, String
from .database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = {"schema": "info"}  # PostgreSQL schema

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_subscribed = Column(Boolean, default=False, nullable=False)
    stripe_customer_id = Column(String, unique=True, nullable=True)
    refresh_token = Column(String, nullable=True)

    def __repr__(self):
        return (
            f"<UserProfile(username='{self.username}', "
            f"subscribed={self.is_subscribed}, "
            f"stripe_customer_id={self.stripe_customer_id})>"
        )

from pydantic import UUID4, BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from constants import UserRole
from .follow import GetFollower


class UserCreate(BaseModel):
    username: str = Field(min_length=2)
    email: EmailStr
    password: str
    bio: Optional[str] = Field(default=None)
    avatar: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )
    user_role: UserRole = Field(default=UserRole.USER, nullable=False)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserEmailUpdate(BaseModel):
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)


class GetUserResponse(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    account_id: UUID4
    username: str
    email: EmailStr
    bio: Optional[str] = None
    avatar: Optional[str] = None
    user_type: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

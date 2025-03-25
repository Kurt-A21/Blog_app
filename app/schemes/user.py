from pydantic import UUID4, BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from app.constants import UserRole


class UserCreate(BaseModel):
    username: str = Field(min_length=2)
    email: EmailStr
    password: str
    bio: Optional[str] = Field(default=None)
    avatar: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )
    user_type: UserRole = Field(default=UserRole.USER)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserEmailUpdate(BaseModel):
    email: Optional[EmailStr] = None

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

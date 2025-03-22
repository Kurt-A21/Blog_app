from pydantic import UUID4, BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enums import UserRole

class UserCreate(BaseModel):
    username: str = Field(min_length=2)
    email: EmailStr
    password: str
    bio: Optional[str] = Field(default=None)
    avatar: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )
    user_type: UserRole = Field(default=UserRole.USER)

    class Config:
        orm_mode = True
        
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    
    @field_validator("email", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        return None if value == "" else value
    
    class Config:
        orm_mode = True
        
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
    
    class Config:
        orm_mode = True
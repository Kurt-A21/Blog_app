from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class UsersRequest(BaseModel):
    username: str = Field(min_length=2)
    email: str = Field(min_length=4)
    password: str = Field(min_length=8)
    bio: Optional[str] = Field(min_length=5, max_length=150, default=None)
    avatar: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))


class PostsResquest(BaseModel):
    content: str = Field(min_length=1)
    image_url: Optional[str] = Field(
        description="Image is not needed to create a post", default=None
    )
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

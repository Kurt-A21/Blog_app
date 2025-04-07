from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .comments import Comment

class PostCreate(BaseModel):
    content: str = Field(min_length=0, max_length=280)
    image_url: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )

    model_config = ConfigDict(from_attributes=True)


class PostUpdate(BaseModel):
    content: Optional[str] = Field(min_length=0, max_length=280)
    image_url: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )

    model_config = ConfigDict(from_attributes=True)


class PostResponse(BaseModel):
    created_by: str = Field(min_length=0)
    content: str = Field(min_length=0, max_length=280)
    image_url: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )
    created_at: datetime
    comments: list[Comment] = []

    model_config = ConfigDict(from_attributes=True)
    
class CreatePostResponse(BaseModel):
    detail: str
    post_details: PostResponse
    
    model_config = ConfigDict(from_attributes=True)


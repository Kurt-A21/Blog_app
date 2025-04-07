from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


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
    owner_username: str = Field(min_length=0)
    content: str = Field(min_length=0, max_length=280)
    image_url: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )

class CreatePostResponse(BaseModel):
    detail: str
    post_details: PostResponse


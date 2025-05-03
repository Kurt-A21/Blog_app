from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from .comments import GetComments
from .reply import GetReplies
from .reactions import ReactionListResponse


class PostCreate(BaseModel):
    tagged_users: Optional[List[str]] = []
    post_content: str = Field(min_length=0, max_length=280)

    model_config = ConfigDict(from_attributes=True)


class PostUpdate(BaseModel):
    post_content: Optional[str] = Field(min_length=0, max_length=280)

    model_config = ConfigDict(from_attributes=True)


class UserTag(BaseModel):
    tagged_users: Optional[List[str]] = []

    model_config = ConfigDict(from_attributes=True)


class PostResponse(BaseModel):
    id: int
    created_by: str = Field(min_length=0)
    tagged_users: Optional[List[str]] = []
    post_content: str = Field(min_length=0, max_length=280)
    image_url: Optional[str] = Field(
        description="Image is not needed to create a account", default=None
    )
    created_at: Optional[datetime] = None
    reaction_count: Optional[int] = None
    reactions: Optional[List[ReactionListResponse]] = []
    comment_count: Optional[int] = None
    comments: Optional[List[GetComments]] = []
    reply_count: Optional[int] = None
    reply: Optional[List[GetReplies]] = []

    model_config = ConfigDict(from_attributes=True)


class CreatePostResponse(BaseModel):
    detail: str
    post_details: PostResponse

    model_config = ConfigDict(from_attributes=True)

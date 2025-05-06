from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from .reactions import GetReactions
from .reply import GetReplies


class GetComments(BaseModel):
    id: int
    created_by: str
    comment_content: str = Field(min_length=0, max_length=280)
    created_at: datetime
    reaction_count: Optional[int]
    reactions: Optional[List[GetReactions]] = []
    reply_count: Optional[int] = None
    reply: Optional[List[GetReplies]] = []

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    comment_content: str = Field(min_length=0, max_length=280)

    model_config = ConfigDict(from_attributes=True)


class CommentUpdate(BaseModel):
    comment_content: str = Field(min_length=0, max_length=280)

    model_config = ConfigDict(from_attributes=True)


class CommentUpdateResponse(BaseModel):
    detail: str
    comment_content: str = Field(min_length=0, max_length=280)
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    detail: str
    post_id: int
    post_content: str
    comment_id: int
    comment_content: str = Field(min_length=0, max_length=280)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

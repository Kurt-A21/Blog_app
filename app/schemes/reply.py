from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from .reactions import GetReactions


class GetReplies(BaseModel):
    id: int
    created_by: str
    reply_content: str = Field(min_length=0, max_length=280)
    created_at: datetime
    reaction_count: Optional[int]
    reactions: Optional[List[GetReactions]] = []

    model_config = ConfigDict(from_attributes=True)


class ReplyCreate(BaseModel):
    reply_content: str

    model_config = ConfigDict(from_attributes=True)


class ReplyUpdateResponse(BaseModel):
    detail: str
    reply_content: str = Field(min_length=0, max_length=280)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReplyResponse(BaseModel):
    detail: str
    post_id: int
    post_content: str
    comment_id: int
    comment_content: str = Field(min_lengsth=0, max_length=280)
    reply_id: int
    reply_content: str = Field(min_length=0, max_length=280)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

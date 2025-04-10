from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class GetComments(BaseModel):
    id: int
    created_by: str
    content: str = Field(min_length=0, max_length=280)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    content: str = Field(min_length=0, max_length=280)

    model_config = ConfigDict(from_attributes=True)


class CommentUpdate(BaseModel):
    detail: str
    content: str = Field(min_length=0, max_length=280)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    detail: str
    post_content: str
    content: str = Field(min_lengsth=0, max_length=280)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

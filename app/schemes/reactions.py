from pydantic import BaseModel, ConfigDict
from app.constants import ReactionType
from typing import Optional


class Reaction(BaseModel):
    reaction_type: ReactionType

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"reaction_type": "like or love or haha or hate or sad"}
        },
    )


class GetReactions(BaseModel):
    id: int
    owner: str
    reaction_type: ReactionType

    model_config = ConfigDict(from_attributes=True)


class ReactionResponse(BaseModel):
    detail: str
    post_content: str
    comment_content: Optional[str] = None
    reply_content: Optional[str] = None
    reaction_type: ReactionType

    model_config = ConfigDict(from_attributes=True)


class ReactionListResponse(BaseModel):
    id: int
    owner: str
    reaction_type: ReactionType

    model_config = ConfigDict(from_attributes=True)

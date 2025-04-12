from pydantic import BaseModel, ConfigDict, Field
from constants import ReactionType


class Reaction(BaseModel):
    reaction_type: ReactionType

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"reaction_type": "like or love or haha or hate or sad"}
        },
    )

class ReactionResponse(BaseModel):
    detail: str
    post_content: str
    reaction_type: ReactionType

    model_config = ConfigDict(from_attributes=True)
    
class ReactionListResponse(BaseModel):
    owner: str
    reaction_type: ReactionType
    
    model_config = ConfigDict(from_attributes=True)

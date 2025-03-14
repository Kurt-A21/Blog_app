from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class PostsResquest(BaseModel):
    content: str = Field(min_length=1)
    image_url: Optional[str] = Field(
        description="Image is not needed to create a post", default=None
    )
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

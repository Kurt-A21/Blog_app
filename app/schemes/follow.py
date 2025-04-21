from pydantic import BaseModel, ConfigDict


class GetFollower(BaseModel):
    user_id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class FollowUser(BaseModel):
    detail: str

    model_config = ConfigDict(from_attributes=True)

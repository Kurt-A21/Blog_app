from pydantic import BaseModel, ConfigDict
from typing import List


class GetFollower(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class GetFollowers(BaseModel):
    followers: List[GetFollower] = []

    model_config = ConfigDict(from_attributes=True)


class GetFollowing(BaseModel):
    following: List[GetFollower] = []

    model_config = ConfigDict(from_attributes=True)


class FollowUser(BaseModel):
    detail: str

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ResetPassword(BaseModel):
    new_password: str = Field(min_length=8, max_length=64)

    model_config = ConfigDict(from_attributes=True)

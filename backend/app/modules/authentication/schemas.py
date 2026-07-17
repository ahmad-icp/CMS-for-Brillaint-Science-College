from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=255)
    college_id: str = Field(min_length=1, max_length=64)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32)

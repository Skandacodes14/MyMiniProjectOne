from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.SystemConfiguration import UserRoles

class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=72, description="Username")
    password: str = Field(..., min_length=6, max_length=72, description="Password")
    role: UserRoles = Field(default=UserRoles.MEMBER, description="UserRoles")

class UserResponseSchema(BaseModel):
    id: int
    username: str
    role: UserRoles

    model_config = ConfigDict(from_attributes=True)

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

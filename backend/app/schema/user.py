from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    email: EmailStr = Field(..., max_length=255)

    @field_validator("name")
    @classmethod
    def strip_and_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        return v



class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    created_at: datetime


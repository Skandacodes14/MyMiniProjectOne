from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class BookBaseSchema(BaseModel):

    title: str = Field(..., min_length=1, max_length=100, description="Book title", examples=["The Ramayana"])
    author: str = Field(..., min_length=1, max_length=100, description="Book author", examples=["Author's full name"])
    genre: str = Field(..., min_length=1, max_length=100, description="Book genre", examples=["Sci-fi"])
    pages: int = Field(..., gt=0, lt=10000, description="Total page count")

class BookCreateSchema(BookBaseSchema):
    pass

class UpdateBookSchema(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    genre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    pages: Optional[int] = Field(default=None, gt=0, lt=10000)
    is_deleted: Optional[bool] = Field(default=None)

class BookResponseSchema(BookBaseSchema):
    id: int
    is_deleted: bool
    is_issued: bool

    model_config = ConfigDict(from_attributes=True)
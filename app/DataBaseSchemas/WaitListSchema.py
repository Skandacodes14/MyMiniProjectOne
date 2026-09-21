from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.DataBaseSchemas.BookSchema import BookResponseSchema

class WaitListRequestSchema(BaseModel):
    book_id: int = Field(..., description="ID of the book to reserve/wait_list")

class WaitListResponseSchema(BaseModel):
    id: int
    user_id: int
    book_id: int
    reserved_at: datetime
    book_record: Optional[BookResponseSchema] = None

    model_config = ConfigDict(from_attributes=True)
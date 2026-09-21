from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.DataBaseSchemas.BookSchema import BookResponseSchema

class BorrowRequestSchema(BaseModel):
    book_id: int = Field(..., description="Book id")

class BorrowResponseSchema(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    return_date: Optional[datetime] = None
    fine_amount: float
    book_record: Optional[BookResponseSchema] = None

    model_config = ConfigDict(from_attributes=True)

class BorrowReturnResponseSchema(BaseModel):
    id: int
    user_id: int
    book_id: int
    return_date: datetime
    days_borrowed: int
    fine_amount: float
    message: str
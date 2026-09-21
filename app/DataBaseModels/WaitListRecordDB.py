from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.DataBaseConnectionInfra import Base

class WaitListRecordDB(Base):
    __tablename__ = "wait_lists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    reserved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_record = relationship("UserRecordDB", back_populates="wait_list_records")
    book_record = relationship("BookRecordDB", back_populates="wait_list_records")

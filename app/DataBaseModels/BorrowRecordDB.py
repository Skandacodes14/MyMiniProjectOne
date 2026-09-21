from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.DataBaseConnectionInfra import Base


class BorrowRecordDB(Base):
    __tablename__ = "borrows"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    issue_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    return_date = Column(DateTime, nullable=True)
    fine_amount = Column(Float, default=0.0)

    user_record = relationship("UserRecordDB", back_populates="borrow_records")
    book_record = relationship("BookRecordDB", back_populates="borrow_records")

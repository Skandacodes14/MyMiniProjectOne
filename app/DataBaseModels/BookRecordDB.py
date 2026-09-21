from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.DataBaseConnectionInfra import Base

class BookRecordDB(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    pages = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_issued = Column(Boolean, default=False)

    borrow_records = relationship("BorrowRecordDB", back_populates="book_record", cascade="all, delete-orphan")
    wait_list_records = relationship("WaitListRecordDB", back_populates="book_record", cascade="all, delete-orphan")

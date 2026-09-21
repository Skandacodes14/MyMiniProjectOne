from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.SystemConfiguration import UserRoles
from app.DataBaseConnectionInfra import Base


class UserRecordDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRoles.MEMBER.value, nullable=False)

    borrow_records = relationship("BorrowRecordDB", back_populates="user_record", cascade="all, delete-orphan")
    wait_list_records = relationship("WaitListRecordDB", back_populates="user_record", cascade="all, delete-orphan")

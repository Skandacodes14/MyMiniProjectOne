from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.DataBaseConnectionInfra import get_db
from app.DataBaseModels import UserRecordDB, BookRecordDB
from app.DataBaseSchemas import (BorrowRequestSchema, BookResponseSchema, BorrowReturnResponseSchema)
from app.LibraryServices import BorrowServices
from app.LibraryServices import AuthenticationServices as auth

router = APIRouter(
    prefix="/loans",
    tags=["Loans & Borrowing"]
)

@router.post(
    "/borrow",
    response_model=BookResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Borrow a book or queue for reservation"
)
def borrow_book(
    payload: BorrowRequestSchema,
    db: Session = Depends(get_db),
    current_user: UserRecordDB = Depends(auth.get_current_user),
):
    return BorrowServices.issue_book_to_member(
        db=db,
        user_id=current_user.id,
        book_id=payload.book_id,
    )

@router.post(
    "/return",
    response_model=BorrowReturnResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Return a borrowed book",
)
def return_book(
    payload: BorrowRequestSchema,
    db: Session = Depends(get_db),
    current_user: UserRecordDB = Depends(auth.get_current_user),
):
    return BorrowServices.receive_book_from_member(
        db=db,
        user_id=current_user.id,
        book_id=payload.book_id,
    )

@router.get(
    "/my-books",
    response_model=List[BookResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List all currently borrowed books for the logged-in member"
)
def get_my_active_borrows(
    db: Session = Depends(get_db),
    current_user: UserRecordDB = Depends(auth.get_current_user)
):
    return db.query(BookRecordDB).filter(
        BookRecordDB.user_id == current_user.id,
        BookRecordDB.return_date == None
    ).all()

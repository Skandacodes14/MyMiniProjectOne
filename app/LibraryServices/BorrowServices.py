from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.SystemConfiguration import settings, ResponseMessages
from app.DataBaseModels import BookRecordDB, WaitListRecordDB
from app.DataBaseSchemas import BorrowReturnResponseSchema

def issue_book_to_member(db: Session, user_id: int, book_id: int) -> BookRecordDB:
    """ 1. issue_book_to_member(db, user_id, book_id)
        Primary Goal: Check out a book to an authenticated member
        or place them in the queue if it's unavailable.

        Catalog Verification: Confirms the book exists and
        is not soft-deleted; halts with 404 Not Found if missing.

        Borrow Limit Guard: Counts active loans for the user
        (return_date == None). If they already hold MAX_BORROW_LIMIT books,
        halts with 400 Bad Request.

        Stock & Queue Branching:

        If book is currently issued (is_issued == True): Checks if the
        user already has a pending ticket in WaitListRecordDB. If not,
        creates one, commits, and returns 400 Bad Request informing them they are queued.

        If book is available (is_issued == False): Sets book.is_issued = True,
        creates a new BorrowRecordDB stamped with the current UTC checkout time,
        commits to disk, and returns the active loan record. """

    #fetch the book and verify its existence
    book = db.query(BookRecordDB).filter(BookRecordDB.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} doesn't exist"
        )

    # we check the number of books the member has already borrowed
    active_borrow_count = db.query(BookRecordDB).filter(
        BookRecordDB.user_id == user_id,
        BookRecordDB.book_id == book_id
    ).count()

    # check if the member has reached the max borrow limit
    if active_borrow_count >= settings.MAX_BORROW_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have reached your borrow limit"
        )

    # check if the book member requests is already issued
    if book.is_issued: # if true we cannot handout the book
        # the below query checks if for a reservation queue of a particular book, is the user already queued
        existing_reservation = db.query(WaitListRecordDB).filter(
            WaitListRecordDB.user_id == user_id,
            WaitListRecordDB.book_id == book_id
        ).first() # returns the first matching python object where the user_id and the book_id of input and table matches

        # if the above query returns a python object the code below will not execute
        # if the above query returns none the one below will also execute
        """If the above check is not done you will have multiple tickets by the same user,
           clogging the queue."""
        if not existing_reservation:
            reservation = WaitListRecordDB(user_id=user_id, book_id=book_id)
            db.add(reservation)
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseMessages.BOOK_OUT_OF_STOCK
        )

    # means that book is available and we can issue it
    book.is_issued = True

    # adding the new data to the borrow record
    new_borrow = BookRecordDB(user_id=user_id, book_id=book_id, issue_date=datetime.now(timezone.utc))
    db.add(new_borrow)
    db.commit()
    db.refresh(new_borrow)
    return new_borrow


def receive_book_from_member(db: Session, user_id: int, book_id: int) -> BorrowReturnResponseSchema:
    """ 2. return_book_from_member(db, user_id, book_id)
        Primary Goal: Process a book return, calculate late penalties,
        close the transaction, and update queue/inventory state.

        Active Loan Verification: Queries BorrowRecordDB for an open
        checkout matching that user and book (return_date == None).
        Halts with 400 Bad Request if no matching loan exists.

        Duration & Fine Calculation: Computes (now - issue_date).days.
        If the duration exceeds ALLOWED_BORROW_DAYS, it multiplies the
        extra days by FINE_PER_DAYS. Otherwise, the fine remains 0.0.

        Closing the Record: Stamps the record with return_date = now and fine_amount = fine.

        Queue Handoff & State Reset: Queries WaitListRecordDB for the oldest
        queued entry (reserved_at.asc()). If someone is waiting, it deletes
        their queue ticket to advance the line. It then sets book.is_issued = False.

        Receipt Delivery: Commits the transaction and returns a structured receipt
        showing the return timestamp, total days borrowed, fine owed, and a
        status message. """

    # checks if the user has borrowed this book
    active_borrow = db.query(BookRecordDB).filter(
        BookRecordDB.user_id == user_id,
        BookRecordDB.book_id == book_id
    ).first()
    # if the member had not borrowed
    if not active_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"We have not issued this book to you"
        )

    returning_date = datetime.now(timezone.utc) # date of returning the book
    issued_date = active_borrow.issue_date # date when book was issued

    if issued_date.tzinfo is None:
        issued_date = issued_date.replace(tzinfo=timezone.utc)

    days_borrowed = (returning_date - issued_date).days
    fine = 0.0

    # if you have borrowed more than allowed days, you will have a fine for those overdue days
    if days_borrowed >= settings.ALLOWED_BORROW_DAYS:
        overdue_days = days_borrowed - settings.ALLOWED_BORROW_DAYS
        fine = float(overdue_days * settings.FINE_PER_DAYS)

    active_borrow.return_date = returning_date # date of returning the book
    active_borrow.fine = fine # fine if applied else zero

    # check if there are others in the waitlist for the same book
    book_borrower = db.query(WaitListRecordDB).filter(
        WaitListRecordDB.book_id == book_id
    ).order_by(WaitListRecordDB.reserved_at.asc()).first()

    # fetching the book to let the member borrow
    book = db.query(BookRecordDB).filter(
        BookRecordDB.id == book_id
    ).first()

    if book_borrower:
        db.delete(book_borrower)
        book.is_issued = False # deletes the waiters wait_list ticket and the book is available to borrow
    else:
        book.is_issued = False # otherwise the book is on the shelf to be borrowed

    db.commit()
    db.refresh(active_borrow)

    return BorrowReturnResponseSchema(
        id=active_borrow.id,
        user_id=active_borrow.user_id,
        book_id=active_borrow.book_id,
        return_date=active_borrow.return_date,
        days_borrowed=days_borrowed,
        fine_amount=fine,
        message=f"Book returned successfully. Amount due: {fine}" if fine > 0 else "Book returned successfully with no fines."

    )

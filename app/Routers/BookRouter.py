from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

import app.SystemConfiguration as config
from app.DataBaseConnectionInfra import get_db
from app.DataBaseModels import UserRecordDB, BookRecordDB
from app.DataBaseSchemas import (BookResponseSchema, BookCreateSchema, UpdateBookSchema)
from app.LibraryServices import AuthenticationServices as auth

router = APIRouter(
    prefix="/books",
    tags=["Books"],
)

@router.get(
    "/",
    response_model=List[BookResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get all books based on search criteria",
)
def list_books(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, gt=0, le=100),
    author: Optional[str] = Query(default=None),
    genre: Optional[str] = Query(default=None),
    title: Optional[str] = Query(default=None),
    pages: Optional[int] = Query(default=None, gt=0),
    is_deleted: Optional[bool] = Query(default=False),
    sort_by: Optional[config.SortField] = Query(default=None),
    order: config.SortOrder = Query(default=config.SortOrder.ASC),
    db: Session = Depends(get_db),
):
    query = db.query(BookRecordDB)

    if author:
        query = query.filter(BookRecordDB.author.ilike(f"%{author}%"))

    if genre:
        query = query.filter(BookRecordDB.genre.ilike(f"%{genre}%"))

    if title:
        query = query.filter(BookRecordDB.title.ilike(f"%{title}%"))

    if pages:
        query = query.filter(BookRecordDB.pages <= pages)

    if is_deleted:
        query = query.filter(BookRecordDB.is_deleted == is_deleted)

    if sort_by:
        column_map = {
            config.SortField.ID: BookRecordDB.id,
            config.SortField.TITLE: BookRecordDB.title,
            config.SortField.AUTHOR: BookRecordDB.author,
            config.SortField.GENRE: BookRecordDB.genre,
            config.SortField.PAGES: BookRecordDB.pages,
            config.SortField.IS_DELETED: BookRecordDB.is_deleted,
        }
        target_column = column_map[sort_by]
        sort_expr = desc(target_column) if order.value == config.SortOrder.DESC.value else asc(target_column)
        query = query.order_by(sort_expr)

    return query.offset(skip).limit(limit).all()

@router.get(
    "/{book_id}",
    response_model=BookResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get a book",
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    book = db.query(BookRecordDB).filter(BookRecordDB.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )
    return book

@router.post(
    "/",
    response_model=BookResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
)
def create_book(
    book: BookCreateSchema,
    db: Session = Depends(get_db),
    admin_user: UserRecordDB = Depends(auth.get_current_admin_user)
):
    db_book = BookRecordDB(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.put(
    "/{book_id}",
    response_model=BookResponseSchema,
    summary="Update a book",
)
def update_book(
    book_id: int,
    updated_book: BookCreateSchema,
    db: Session = Depends(get_db),
    admin_user: UserRecordDB = Depends(auth.get_current_admin_user)):
    book = db.query(BookRecordDB).filter(BookRecordDB.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )
    for key, value in updated_book.model_dump().items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book

@router.patch(
    "/{book_id}",
    response_model=BookResponseSchema,
    summary="Partially update a book",
)
def partial_update_book(
    book_id: int,
    updated_book: UpdateBookSchema,
    db: Session = Depends(get_db),
    admin_user: UserRecordDB = Depends(auth.get_current_admin_user)
):
    book = db.query(BookRecordDB).filter(
        BookRecordDB.id == book_id
    ).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )

    patch_data = updated_book.model_dump(exclude_unset=True)
    for key, value in patch_data.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book

@router.delete(
    "/{book_id}",
    summary="Delete a book",
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    admin_user: UserRecordDB = Depends(auth.get_current_admin_user)
):
    book = db.query(BookRecordDB).filter(
        BookRecordDB.id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )
    title = book.title
    db.delete(book)
    db.commit()
    return {"Message": f"Book '{title}' has been deleted"}

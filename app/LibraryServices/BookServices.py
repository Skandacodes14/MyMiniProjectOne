from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
import app.DataBaseModels as DB
import app.DataBaseSchemas as schemas
import app.DataBaseConnectionInfra as DBCI
import app.SystemConfiguration as config
import app.LibraryServices.AuthenticationServices as auth

app = FastAPI()

@app.get("/books/", response_model=List[schemas.BookResponseSchema])
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
    db: Session = Depends(DBCI.get_db),
):
    query = db.query(DB.BookRecordDB)

    if author:
        query = query.filter(DB.BookRecordDB.author.ilike(f"%{author}%"))
    if genre:
        query = query.filter(DB.BookRecordDB.genre.ilike(f"%{genre}%"))
    if title:
        query = query.filter(DB.BookRecordDB.title.ilike(f"%{title}%"))
    if pages:
        query = query.filter(DB.BookRecordDB.pages <= pages)
    if is_deleted:
        query = query.filter(DB.BookRecordDB.is_deleted == False)

    if sort_by:
        column_map = {
            config.SortField.ID: DB.BookRecordDB.id,
            config.SortField.TITLE: DB.BookRecordDB.title,
            config.SortField.AUTHOR: DB.BookRecordDB.author,
            config.SortField.GENRE: DB.BookRecordDB.genre,
            config.SortField.PAGES: DB.BookRecordDB.pages,
            config.SortField.IS_DELETED: DB.BookRecordDB.is_deleted,
        }
        target_column = column_map[sort_by]
        sort_expr = desc(target_column) if order.value == config.SortOrder.DESC.value else asc(target_column)
        query = query.order_by(sort_expr)

    return query.offset(skip).limit(limit).all()

@app.get("/books/{book_id}", response_model=schemas.BookResponseSchema)
def get_book(book_id: int, db: Session = Depends(DBCI.get_db)):
    book = db.query(DB.BookRecordDB).filter(DB.BookRecordDB.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )
    return book

@app.post("/books/", response_model=schemas.BookResponseSchema, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreateSchema, db: Session = Depends(DBCI.get_db), admin_user: DB.UserRecordDB = Depends(auth.get_current_admin_user)):
    db_book = DB.BookRecordDB(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.put("/books/{book_id}", response_model=schemas.BookResponseSchema)
def update_book(book_id: int, updated_book: schemas.BookCreateSchema, db: Session = Depends(DBCI.get_db), admin_user: DB.UserRecordDB = Depends(auth.get_current_admin_user)):
    book = db.query(DB.BookRecordDB).filter(DB.BookRecordDB.id == book_id).first()
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

@app.patch("/books/{book_id}", response_model=schemas.BookResponseSchema)
def partial_update_book(book_id: int, updated_book: schemas.UpdateBookSchema, db: Session = Depends(DBCI.get_db), admin_user: DB.UserRecordDB = Depends(auth.get_current_admin_user)):
    book = db.query(DB.BookRecordDB).filter(DB.BookRecordDB.id == book_id).first()
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

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(DBCI.get_db), admin_user: DB.UserRecordDB = Depends(auth.get_current_admin_user)):
    book = db.query(DB.BookRecordDB).filter(DB.BookRecordDB.id == book_id).first()
    db.delete(book)
    db.commit()
    return {"Message": f"Book '{book.title}' has been deleted"}
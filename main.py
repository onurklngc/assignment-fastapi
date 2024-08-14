import os
from datetime import datetime, timedelta
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi import Request
from fastapi.params import Query
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database_config import DatabaseConfig
from src.model import Book, Patron
from src.model_dto import BookCreateDto, BookUpdateDto, BookDto, PatronDto, PatronUpdateDto, \
    PatronCreateDto

load_dotenv()

database_url = os.getenv("DATABASE_URL")
database_config = DatabaseConfig(database_url=database_url)

app = FastAPI()


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred. Please try again later."},
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/books/", response_model=BookDto)
def create_book(book: BookCreateDto, db: Session = Depends(database_config.get_db)):
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    return db_book


@app.get("/books", response_model=list[BookDto])
def list_books(db: Session = Depends(database_config.get_db)):
    books = db.query(Book).all()
    return books


@app.get("/books/{book_id}", response_model=BookDto)
def get_book(book_id: int, db: Session = Depends(database_config.get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=BookDto)
def update_book(book_id: int, book_update: BookUpdateDto, db: Session = Depends(database_config.get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(book, key, value)

    db.commit()
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(database_config.get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"ok": True}


@app.post("/patrons/", response_model=PatronDto)
def create_patron(patron: PatronCreateDto, db: Session = Depends(database_config.get_db)):
    patron_data = patron.model_dump()
    if not patron_data["membership_start_date"]:
        patron_data["membership_start_date"] = datetime.utcnow()
    new_patron = Patron(**patron_data)
    db.add(new_patron)
    db.commit()
    return new_patron


@app.get("/patrons", response_model=list[PatronDto])
def list_patrons(db: Session = Depends(database_config.get_db)):
    patrons = db.query(Patron).all()
    return patrons


@app.get("/patrons/{patron_id}", response_model=PatronDto)
def get_patron(patron_id: int, db: Session = Depends(database_config.get_db)):
    patron = db.query(Patron).filter(Patron.id == patron_id).first()
    if patron is None:
        raise HTTPException(status_code=404, detail="Patron not found")
    return patron


@app.put("/patrons/{patron_id}", response_model=PatronDto)
def update_patron(patron_id: int, patron_update: PatronUpdateDto, db: Session = Depends(database_config.get_db)):
    patron = db.query(Patron).filter(Patron.id == patron_id).first()
    if patron is None:
        raise HTTPException(status_code=404, detail="Patron not found")
    update_data = patron_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patron, key, value)

    db.commit()
    return patron


@app.delete("/patrons/{patron_id}")
def delete_patron(patron_id: int, db: Session = Depends(database_config.get_db)):
    patron = db.query(Patron).filter(Patron.id == patron_id).first()
    if patron is None:
        raise HTTPException(status_code=404, detail="Patron not found")
    db.delete(patron)
    db.commit()
    return {"ok": True}


@app.post("/checkout/{book_id}/patron/{patron_id}", response_model=BookDto)
def checkout_book(book_id: int, patron_id: int,
                  checkout_period: Optional[int] = Query(default=14, description="Checkout period in days"),
                  db: Session = Depends(database_config.get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    patron = db.query(Patron).filter(Patron.id == patron_id).first()
    if book is None or patron is None:
        raise HTTPException(status_code=404, detail="Book or Patron not found")
    if book.is_checked_out:
        raise HTTPException(status_code=400, detail="Book already checked out")
    book.is_checked_out = True
    book.due_date = datetime.utcnow() + timedelta(days=checkout_period)
    book.patron_id = patron_id
    db.commit()
    return book


@app.post("/return/{book_id}", response_model=BookDto)
def return_book(book_id: int, db: Session = Depends(database_config.get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None or not book.is_checked_out:
        raise HTTPException(status_code=404, detail="Book not found or not checked out")
    book.is_checked_out = False
    book.due_date = None
    book.patron_id = None
    db.commit()
    return book


@app.get("/books/checkedout/", response_model=list[BookDto])
def list_checked_out_books(db: Session = Depends(database_config.get_db)):
    books = db.query(Book).filter(Book.is_checked_out is True).all()
    return books


@app.get("/books/patron/{patron_id}", response_model=list[BookDto])
def list_books_by_patron(patron_id: int, db: Session = Depends(database_config.get_db)):
    books = db.query(Book).filter(Book.patron_id == patron_id).all()
    return books


@app.get("/books/overdue/", response_model=list[BookDto])
def list_overdue_books(db: Session = Depends(database_config.get_db)):
    now = datetime.utcnow()
    books = db.query(Book).filter(Book.due_date < now, Book.is_checked_out is True).all()
    return books


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)

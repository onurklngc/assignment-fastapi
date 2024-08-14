import datetime
from typing import Optional

from pydantic import BaseModel, constr, field_validator

from src.util import is_valid_isbn, is_valid_email


class BookCreateDto(BaseModel):
    title: constr(max_length=255)
    author: constr(max_length=255)
    isbn: Optional[constr(max_length=17)] = None
    published_year: Optional[int] = None

    @field_validator('isbn')
    def validate_isbn_field(cls, isbn: str):
        if isbn and not is_valid_isbn(isbn):
            raise ValueError("Invalid ISBN")
        return isbn


class BookUpdateDto(BookCreateDto):
    title: Optional[constr(max_length=255)] = None
    author: Optional[constr(max_length=255)] = None
    isbn: Optional[constr(max_length=17)] = None
    published_year: Optional[int] = None
    due_date: Optional[datetime.datetime] = None


class BookDto(BookCreateDto):
    id: int
    is_checked_out: bool
    due_date: Optional[datetime.datetime]
    patron_id: Optional[int]

    class ConfigDict:
        from_attributes = True


class PatronCreateDto(BaseModel):
    name: constr(max_length=255)
    phone_number: Optional[constr(max_length=20)] = None
    email: constr(max_length=255)
    membership_start_date: Optional[datetime.datetime] = None

    @field_validator('email')
    def validate_email_field(cls, email: str):
        if not is_valid_email(email):
            raise ValueError("Invalid email address")
        return email


class PatronUpdateDto(PatronCreateDto):
    name: Optional[constr(max_length=255)] = None
    phone_number: Optional[constr(max_length=20)] = None
    email: Optional[constr(max_length=255)] = None
    membership_start_date: Optional[datetime.datetime] = None


class PatronDto(PatronCreateDto):
    id: int
    membership_start_date: datetime.datetime

    class ConfigDict:
        from_attributes = True

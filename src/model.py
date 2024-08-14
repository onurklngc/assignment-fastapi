from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    author = Column(String(255), index=True)
    isbn = Column(String(17), index=True, nullable=True)
    published_year = Column(Integer, nullable=True)
    is_checked_out = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True)
    patron_id = Column(Integer, ForeignKey("patrons.id"), nullable=True)


class Patron(Base):
    __tablename__ = "patrons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    phone_number = Column(String(20))
    email = Column(String(255))
    membership_start_date = Column(DateTime)
    checked_out_books = relationship("Book", backref="patron")

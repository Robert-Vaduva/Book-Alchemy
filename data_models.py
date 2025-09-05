"""
Database models for a simple library application using Flask-SQLAlchemy.

This module defines two ORM models:
- Author: Represents an author with basic biographical details (name, birth and death dates).
          Each author can be associated with multiple books.
- Book:   Represents a book entry in the library, including ISBN, title,
          publication year, optional cover URL, and a reference to its author.

The Author ↔ Book relationship is one-to-many:
- One author can have many books.
- Each book belongs to exactly one author.

These models are intended for use in a Flask application configured with SQLAlchemy.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


db = SQLAlchemy()


class Author(db.Model):  # pylint: disable=too-few-public-methods
    """Represents an author who can have multiple books in the library."""
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    birth_date = Column(String)
    date_of_death = Column(String)
    books = relationship("Book", back_populates="author")

    def __repr__(self):
        return f"Author(id = {self.id}, name = {self.name})"


class Book(db.Model):  # pylint: disable=too-few-public-methods
    """Represents a book entry linked to a specific author."""
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String)
    title = Column(String)
    publication_year = Column(String)
    cover_url = Column(String)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")

    def __repr__(self):
        return f"Book(id = {self.id}, title = {self.title})"

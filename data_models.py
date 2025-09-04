from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    birth_date = Column(String)
    date_of_death = Column(String)
    books = relationship("Book", back_populates="author")

    def __repr__(self):
        return f"Author(id = {self.id}, name = {self.name})"


class Book(db.Model):
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

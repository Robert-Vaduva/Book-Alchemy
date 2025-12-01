"""
Flask Library Management Application

This module implements a simple library system using Flask and SQLAlchemy.
It allows viewing, adding, and deleting books and authors, with optional
search and sorting on the homepage. The database is pre-populated with
some initial books and authors for demonstration purposes.
"""
import os
from data_models import db, Author, Book
from flask import Flask, render_template, request, redirect, url_for, flash
from helpers.json.json_helper import read_json_data
from sqlalchemy.exc import SQLAlchemyError


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.secret_key = "mysecretkey"
db.init_app(app)
PATH = os.path.join('data', 'initial_books.json')


@app.route('/', methods=['GET'])
def home():
    """Render the homepage with optional search and sorting of books."""
    search_query = request.args.get('q', '')  # get the search query from URL
    sort_by = request.args.get('sort_by', 'title')

    books_query = Book.query.join(Book.author)  # join author for searching

    if search_query:
        # filter books by title or author name
        books_query = books_query.filter(
            (Book.title.ilike(f"%{search_query}%")) |
            (Author.name.ilike(f"%{search_query}%"))
        )
    # Apply sorting
    if sort_by == 'title':
        books_query = books_query.order_by(Book.title)
    elif sort_by == 'author':
        books_query = books_query.order_by(Author.name)
    elif sort_by == 'year':
        books_query = books_query.order_by(Book.publication_year)

    books = books_query.all()
    return render_template('home.html', books=books, sort_by=sort_by, search_query=search_query)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Add a new author to the database via a form."""
    if request.method == 'POST':
        try:
            author_name = request.form.get('name')
            author = Author.query.filter(Author.name.ilike(f"%{author_name}%")).first()
            if author:
                flash(f"The author '{author_name}' already exists in the database!", "danger")
            else:
                new_author = Author(name=author_name,
                                    birth_date=request.form.get('birth_date'),
                                    date_of_death=request.form.get('date_of_death'))
                db.session.add(new_author)
                db.session.commit()
                flash(f"Author '{author_name}' was successfully added!", "success")
        except SQLAlchemyError as error:
            print(f"Error while adding the requested author in the database: {error}")
            db.session.rollback()
    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Add a new book to the database via a form."""
    authors = Author.query.all()
    if request.method == 'POST':
        try:
            isbn = request.form.get('isbn')
            book = Book.query.filter(Book.isbn.ilike(f"%{isbn}%")).first()
            if book:
                flash(f"The book with ISBN: '{isbn}' already exists in the database!", "danger")
            else:
                new_book = Book(isbn=isbn,
                                title=request.form.get('title'),
                                publication_year=request.form.get('publication_year'),
                                cover_url=f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg",
                                author_id=request.form.get('author_id'))
                db.session.add(new_book)
                db.session.commit()
                flash(f"Book '{new_book.title}' was successfully added!", "success")
        except SQLAlchemyError as error:
            print(f"Error while adding the requested book in the database: {error}")
            db.session.rollback()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a book by ID and remove its author if they have no other books."""
    book = Book.query.get_or_404(book_id)
    author = book.author  # keep a reference before deleting the book
    db.session.delete(book)
    db.session.commit()
    # If the author has no more books, delete the author too
    if author and not author.books:
        db.session.delete(author)
        db.session.commit()
    flash(f"The book '{book.title}' was successfully deleted!", "success")
    return redirect(url_for('home'))


def init_db():
    """Initialize the database with tables and populate with initial books."""
    # https://openlibrary.org/dev/docs/api/covers
    with app.app_context():
        db.drop_all()  # enable for a fresh copy of the database
        db.create_all()

        initial_books = read_json_data(PATH)
        for book in initial_books:
            author = Author(name=book['author']['name'],
                            birth_date=book['author']['birth_date'],
                            date_of_death=book['author']['date_of_death'])
            db.session.add(author)
            db.session.flush()  # get author.id

            book_1 = Book(title=book['title'],
                          isbn=book['isbn'],
                          publication_year=book['publication_year'],
                          cover_url=book['cover_url'],
                          author_id=author.id)
            db.session.add(book_1)
        db.session.commit()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)

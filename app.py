import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
from flask import Flask, render_template, request, redirect, url_for, flash


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.secret_key = "mysecretkey"
db.init_app(app)
initial_books = [
    {
        "book_id": 1,
        "title": "The Old Man and the Sea",
        "isbn": "9780684801223",
        "publication_year": "1952",
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780684801223-M.jpg",
        "author": {
            "id": 1,
            "name": "Ernest Hemingway",
            "birth_date": "1899-07-21",
            "date_of_death": "1961-07-02"
        }
    },
    {
        "book_id": 2,
        "title": "1984",
        "isbn": "9780451524935",
        "publication_year": "1949",
        "cover_url": "https://ia800505.us.archive.org/view_archive.php?archive=/10/items/m_covers_0011/m_covers_0011_26.zip&file=0011260544-M.jpg",
        "author": {
            "id": 2,
            "name": "George Orwell",
            "birth_date": "1903-06-25",
            "date_of_death": "1950-01-21"
        }
    },
    {
        "book_id": 3,
        "title": "Pride and Prejudice",
        "isbn": "9780141439518",
        "publication_year": "1813",
        "cover_url": "https://ia600703.us.archive.org/view_archive.php?archive=/4/items/m_covers_0008/m_covers_0008_46.zip&file=0008467127-M.jpg",
        "author": {
            "id": 3,
            "name": "Jane Austen",
            "birth_date": "1775-12-16",
            "date_of_death": "1817-07-18"
        }
    },
    {
        "book_id": 4,
        "title": "Crime and Punishment",
        "isbn": "9780486415871",
        "publication_year": "1866",
        "cover_url": "https://ia600505.us.archive.org/view_archive.php?archive=/5/items/m_covers_0012/m_covers_0012_18.zip&file=0012183176-M.jpg",
        "author": {
            "id": 4,
            "name": "Fyodor Dostoevsky",
            "birth_date": "1821-11-11",
            "date_of_death": "1881-02-09"
        }
    },
    {
        "book_id": 5,
        "title": "To Kill a Mockingbird",
        "isbn": "9780061120084",
        "publication_year": "1960",
        "cover_url": "https://ia801601.us.archive.org/view_archive.php?archive=/25/items/m_covers_0014/m_covers_0014_35.zip&file=0014351032-M.jpg",
        "author": {
            "id": 5,
            "name": "Harper Lee",
            "birth_date": "1926-04-28",
            "date_of_death": "2016-02-19"
        }
    },
    {
        "book_id": 6,
        "title": "The Great Gatsby",
        "isbn": "9780743273565",
        "publication_year": "1925",
        "cover_url": "https://ia800502.us.archive.org/view_archive.php?archive=/31/items/m_covers_0013/m_covers_0013_02.zip&file=0013028546-M.jpg",
        "author": {
            "id": 6,
            "name": "F. Scott Fitzgerald",
            "birth_date": "1896-09-24",
            "date_of_death": "1940-12-21"
        }
    }
]


@app.route('/', methods=['GET'])
def home():
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
    if request.method == 'POST':
        new_author = Author(name=request.form.get('name'),
                            birth_date=request.form.get('birth_date'),
                            date_of_death=request.form.get('date_of_death'))
        db.session.add(new_author)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        new_book = Book(isbn=isbn,
                        title=request.form.get('title'),
                        publication_year=request.form.get('publication_year'),
                        cover_url=f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg",
                        author_id=request.form.get('author_id'))
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('add_book.html')


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author  # keep a reference before deleting the book

    db.session.delete(book)
    db.session.commit()

    # If the author has no more books, delete the author too
    if author and not author.books:
        db.session.delete(author)
        db.session.commit()

    flash(f"Book '{book.title}' was successfully deleted!", "success")
    return redirect(url_for('home'))


def init_db():
    # https://openlibrary.org/dev/docs/api/covers
    with app.app_context():
        db.drop_all()  # enable for a fresh copy of the database
        db.create_all()
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
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import os
from datetime import datetime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/library.sqlite')


db.init_app(app)

# # Creating database tables
# with app.app_context():
#     db.create_all()


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name'].strip()
        birth_date = request.form['birth_date']
        date_of_death = request.form['date_of_death']
        
        if birth_date:
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        else:
            return render_template('add_author.html', error="Please fill in the birth date")
        
        if date_of_death:
            date_of_death = datetime.strptime(date_of_death, '%Y-%m-%d').date()
        else:
            date_of_death = None
        
        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        return render_template('add_author.html', success=True)

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']
        
        book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
        db.session.add(book)
        db.session.commit()
        return render_template('add_book.html', success=True)

    return render_template('add_book.html')


@app.route('/')
def home():
    books = Book.query.all()
    book_data = []

    for book in books:
        author = Author.query.get(book.author_id)
        cover_url = f'https://covers.openlibrary.org/b/isbn/{book.isbn}-L.jpg'
        book_data.append({
            'title': book.title,
            'cover_url': cover_url,
            'author': author.name,
            
        })

    return render_template('home.html', book_data=book_data)


if __name__ == "__main__":
    app.run()

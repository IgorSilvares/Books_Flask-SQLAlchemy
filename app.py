from flask import Flask, request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_wtf import FlaskForm
from wtforms import HiddenField
import os
from datetime import datetime




app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.urandom(24)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/library.sqlite')




db.init_app(app)

class DeleteBookForm(FlaskForm):
    book_id = HiddenField('book_id')


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
        if not birth_date:
            return render_template('add_author.html', error="Please fill in the birth date")
        
        if date_of_death:
            date_of_death = datetime.strptime(date_of_death, '%Y-%m-%d').date()
        
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
    search_query = request.args.get('search')
    sort_by = request.args.get('sort_by', 'title')
    print(f"Search query: {search_query}")
    print(f"Sort by: {sort_by}")
    books = Book.query.all()
    book_data = []

    if search_query:
        books = Book.query.join(Author).filter(
            Book.title.ilike(f'%{search_query}%') | 
            Author.name.ilike(f'%{search_query}%') | 
            Book.isbn.ilike(f'%{search_query}%')
        ).all()
        if not books:
            return render_template('home.html', message="No books found.")
    books = Book.query.all()

    if sort_by == 'title':
        books = sorted(books, key=lambda x: x.title)
    elif sort_by == 'author':
        books = sorted(books, key=lambda x: Author.query.get(x.author_id).name)

    for book in books:
        author = Author.query.get(book.author_id)
        cover_url = f'https://covers.openlibrary.org/b/isbn/{book.isbn}-L.jpg'
        book_data.append({
            'id': book.id,
            'title': book.title,
            'cover_url': cover_url,
            'author': author.name,
        })

    return render_template('home.html', book_data=book_data, form=DeleteBookForm())




@app.route('/search', methods=['GET'])
def search():
    return home()



@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        flash("Book deleted successfully!")
    else:
        flash("Book not found!")
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import os
import sqlite3
import base64

bp = Blueprint('BOOKS', __name__)


@bp.route('/')
def index():
    db = get_db()
    sell_number_DESC_books = db.execute(
        'SELECT id, author, title, detail, created, author_id, picture, inventory'
        ' FROM book '
        ' ORDER BY sell_number DESC'
    ).fetchall()
    creat_date_DESC_books = db.execute(
        'SELECT id, author, title, detail, created, author_id, picture, inventory'
        ' FROM book '
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('index.html', sell_DESC_posts=sell_number_DESC_books,
                           date_DESC_posts=creat_date_DESC_books, )


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        number = request.form['number']
        detail = request.form['detail']
        price = request.form['price']
        category = request.form['category']
        picture = request.files['picture']
        error = None

        basePath = os.path.dirname(__file__)  # 当前文件所在路径

        upload_path = os.path.join(basePath, 'static/images', picture.filename)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        # upload_path = os.path.join(basepath, 'static/images','test.jpg')  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        picture.save(upload_path)

        if not title:
            error = 'Title is required.'
        if not price:
            error = 'Title is required.'
        if not author:
            error = 'Title is required.'
        if not number:
            error = 'Title is required.'
        if not detail:
            error = 'Title is required.'
        if not category:
            error = 'Title is required.'
        if not picture:
            error = 'Title is required.'

        if error is not None:
            flash(error)
            return redirect(url_for('BOOKS.create'))
        else:
            db = get_db()
            db.execute(
                'INSERT INTO book (title, author, author_id, inventory, detail, category, picture, price)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (title, author, g.user['id'], number, detail, category, picture.filename, price)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('html/add.html')


def get_book(id, check_author=True):
    book = get_db().execute(
        'SELECT author, title, detail, created, author_id, picture, inventory, price, id'
        ' FROM book WHERE id = ?',
        (id,)
    ).fetchone()

    if book is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return book


@bp.route('/<int:id>/detail', methods=('GET', 'POST'))
def detail(id):
    book = get_book(id)

    db = get_db()
    comments = db.execute(
        'SELECT p.id, title, body, created, author_id, username, book_id'
        ' FROM post p JOIN buyer u ON p.author_id = u.id'
        ' WHERE p.book_id = ?'
        ' ORDER BY created DESC', (book['id'],)
    ).fetchall()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, book_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], book['id'])
            )
            db.commit()
            return redirect('/%d/detail' % (id))

    return render_template('html/detail.html', post=book, comments=comments)


@bp.route('/<int:id>/order', methods=('GET', 'POST'))
@login_required
def order(id):
    book = get_book(id)

    if request.method == 'POST':
        number = request.form['number']
        error = None

        if not number:
            error = 'Title is required.'

        if int(number) > book['inventory']:
            error = 'Not enough'

        if error is not None:
            flash(error)
            return redirect('/%d/detail' % (id))
        else:

            return render_template('html/makeOrder.html', post=book, number=number)


@bp.route('/<int:id>/<int:number>/makeOrder', methods=('GET', 'POST'))
@login_required
def makeOrder(id, number):
    book = get_book(id)

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        address2 = request.form['address2']
        city = request.form['city']
        zip = request.form['zip']
        error = None

        if not name:
            error = 'Title is required.'
        if not phone:
            error = 'Title is required.'
        if not address:
            error = 'Title is required.'
        if not city:
            error = 'Title is required.'
        if not zip:
            error = 'Title is required.'

        if error is not None:
            flash(error)
            return render_template('html/makeOrder.html', post=book, number=number)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO orders (buyer_id, seller_id, book_id, name, address, address2, city, zip, phone, number)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (session.get('user_id'), book['author_id'], id, name, address, address2, city, zip, phone, number))
            db.execute(
                'UPDATE book SET inventory = ?, sell_number = ?'
                ' WHERE id = ?',
                (book['inventory'] - int(number), int(number), book['id'])
            )
            db.commit()

            return redirect(url_for('BOOKS.orders'))


@bp.route('/orders', methods=('GET', 'POST'))
@login_required
def orders():
    if session['user_type'] == 'seller':
        orders = get_db().execute(
            'SELECT buyer_id, seller_id, book_id, p.name, address, address2, city, zip, p.phone, p.number, username, p.created, title'
            ' FROM (orders p JOIN buyer u ON p.buyer_id = u.id) INNER JOIN book b ON p.book_id = b.id'
            ' WHERE seller_id = ?'
            ' ORDER BY p.created DESC',
            (g.user['id'],)
        ).fetchall()
        if orders is None:
            abort(404)
        return render_template('html/orders.html', orders=orders)

    else:
        orders = get_db().execute(
            'SELECT buyer_id, seller_id, book_id, p.name, address, address2, city, zip, p.phone, p.number, u.username, p.created, b.title'
            ' FROM (orders p JOIN seller u ON p.seller_id = u.id) INNER JOIN book b ON p.book_id = b.id'
            ' WHERE buyer_id = ?'
            ' ORDER BY p.created DESC',
            (g.user['id'],)
        ).fetchall()
        if orders is None:
            abort(404)
        return render_template('html/orders.html', orders=orders)


@bp.route('/search', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        search_text = request.form['search']

        db = get_db()
        search = db.execute(
            ' SELECT id, author, title, detail, created, author_id, picture, inventory'
            ' FROM book WHERE title LIKE "%' + search_text + '%"'
                                                             ' ORDER BY created DESC',
        ).fetchall()

    return render_template('html/search.html', result=search)

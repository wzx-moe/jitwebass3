import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/buyerregister', methods=('GET', 'POST'))
def buyerregister():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif db.execute(
                'SELECT id FROM buyer WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO buyer (username, password, email) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), email)
            )
            db.commit()
            return redirect(url_for('index'))

        flash(error)

    return redirect(url_for('index'))


@bp.route('/sellerregister', methods=('GET', 'POST'))
def sellerregister():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif not phone:
            error = 'Phone number is required.'
        elif db.execute(
                'SELECT id FROM seller WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO seller (username, password, email, phone) VALUES (?, ?, ?, ?)',
                (username, generate_password_hash(password), email, phone)
            )
            db.commit()
            return redirect(url_for('index'))

        flash(error)

    return redirect(url_for('index'))


@bp.route('/buyerlogin', methods=('GET', 'POST'))
def buyerlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM buyer WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_type'] = 'buyer'
            return redirect(url_for('index'))

        flash(error)

    return redirect(url_for('index'))


@bp.route('/sellerlogin', methods=('GET', 'POST'))
def sellerlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM seller WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_type'] = 'seller'
            return redirect(url_for('index'))

        flash(error)

    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
        g.userType = None
    else:
        if session.get('user_type') == 'buyer':
            g.user = get_db().execute(
                'SELECT * FROM buyer WHERE id = ?', (user_id,)
            ).fetchone()
            g.userType = 'buyer'
        else:
            g.user = get_db().execute(
                'SELECT * FROM seller WHERE id = ?', (user_id,)
            ).fetchone()
            g.userType = 'seller'




@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view

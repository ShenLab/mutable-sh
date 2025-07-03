import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from mutable.db import get_user_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def nologin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user:
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        password2 = request.form['password2']

        db = get_user_db()
        error = None

        if not username:
            error = 'Username is required'
        else:
            user = db.execute(
                    'SELECT * FROM user WHERE LOWER(username) = ?', (username,)
                ).fetchone()
            
            if not user:
                error = "User not allowed to register"
            elif user['username'] and user['password']:
                error = "User already registered. Please login"
            else:
                if not password:
                    error = 'Password is required'
                elif password != password2:
                    error = 'Passwords do not match'
                else:
                    try:
                        #db.execute(
                        #    "INSERT INTO user (username, password) VALUES (?, ?)",
                        #     (username, generate_password_hash(password)),
                        #)
                        db.execute(
                            "UPDATE user SET password = ? WHERE username = ? AND password is NULL",
                            (generate_password_hash(password), username)
                        )
                        db.commit()

                        session.clear()
                        session['user_id'] = user['id']
                        return redirect(url_for('index'))
                    
                    except db.IntegrityError:
                        error = f"User {username} is already registered or not allowed to register"

        if error:
            flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        error = 'Please use guest login for demo website'

        flash(error)


    return render_template('auth/login.html')

@bp.route('/guest', methods=('POST','GET'))
def guestLogin():
    # dummy username and password assigned to guests
    guest_username = "guest@gmail.com"
    guest_password = "12345678"

    db = get_user_db()
    guest_user = db.execute(
        'SELECT * FROM user WHERE username = ?', (guest_username,)
    ).fetchone()

    if guest_user and check_password_hash(guest_user['password'], guest_password):
        session.clear()
        session['user_id'] = guest_user['id']
        return redirect(url_for('index'))
    else:
        flash('Guest login failed. Please try again.')
        return redirect(url_for('auth.login'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_user_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

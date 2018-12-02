from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm
from app.models import User
from app.instagram import self_info


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    self_info = session['self_info']
    return render_template('index.html', title='Home',
                           self_info=self_info)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None:
            user = User(username=form.username.data)
            user.set_api(password=form.password.data)
            if user.api is None:
                flash('Invalid username or password')
                return redirect(url_for('login'))
            elif user.api == -1:
                flash('For security purposes, Instagram needs to check and \
                    validate your account online')
                return redirect(url_for('login'))
            db.session.add(user)
            db.session.commit()
        else:
            user.set_api(password=form.password.data)
            if user.api is None:
                flash('Invalid username or password')
                return redirect(url_for('login'))
            db.session.commit()

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        session['self_info'] = self_info(user.api)
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

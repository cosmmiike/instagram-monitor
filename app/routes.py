from flask import render_template, flash, redirect, url_for, request, session,\
                  make_response
from flask_login import current_user, login_user, logout_user, login_required
import json

from app import app, db
from app.forms import LoginForm
from app.models import User
from app.instagram import set_instagram_cookies, get_instagram_api, self_info,\
                          get_stories, get_feed


@app.route('/')
@app.route('/index')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    settings = request.cookies.get('instagram-monitor')
    api = get_instagram_api(settings)
    info = self_info(api)['user']
    stories_tray = get_stories(api)['tray'][:5]
    posts_feed = get_feed(api)['feed_items']
    print(json.dumps(posts_feed))
    return render_template('index.html', title='Home', self_info=info,
                           stories=stories_tray, posts=posts_feed)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        settings = request.cookies.get('instagram-monitor')

        if settings is None:
            settings = set_instagram_cookies(username=form.username.data, password=form.password.data)
            if settings is None:
                flash('Invalid username or password')
                return redirect(url_for('login'))
            elif settings == -1:
                flash('For security purposes, Instagram needs to check and validate your access')
                return redirect(url_for('login'))

        api = get_instagram_api(cached_settings=settings)
        if api is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        elif api == -1:
            flash('For security purposes, Instagram needs to check and validate your access')
            return redirect(url_for('login'))
        else:
            resp = make_response(redirect(url_for('login')))
            resp.set_cookie('instagram-monitor', value=settings)
            new_cookies = True

        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User(username=form.username.data)
            db.session.add(user)
            db.session.commit()

        login_user(user, remember=form.remember_me.data)

        if new_cookies:
            return resp

        return redirect(url_for('index'))
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('instagram-monitor', '', expires=0)
    return resp

from flask import render_template, flash, redirect, url_for, request, session,\
                  make_response
from flask_login import current_user, login_user, logout_user, login_required
import json

from app import app, db
from app.forms import LoginForm, DownloadForm
from app.models import User
from app.instagram import set_instagram_cookies, get_instagram_api, self_info,\
                          get_stories_tray, get_feed, user_info, get_stories,\
                          get_posts, get_highligts, get_followings,\
                          link_to_shortcode, link_to_username, get_post_info


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        settings = request.cookies.get('instagram-monitor')
        settings_web = request.cookies.get('instagram-monitor-web')

        if settings is None or settings_web is None:
            settings, settings_web = set_instagram_cookies(username=form.username.data,
                                                           password=form.password.data)
            if settings is None or settings_web is None:
                flash('Invalid username or password -- 1')
                return redirect(url_for('login'))
            elif settings == -1 or settings_web == -1:
                flash('For security purposes, Instagram needs to check and \
                       validate your access')
                return redirect(url_for('login'))

        api, web_api = get_instagram_api(cached_settings=settings,
                                         cached_settings_web=settings_web)
        if api is None or web_api is None:
            flash('Invalid username or password  -- 2')
            return redirect(url_for('login'))
        elif api == -1 or web_api == -1:
            flash('For security purposes, Instagram needs to check and \
                  validate your access')
            return redirect(url_for('login'))
        else:
            resp = make_response(redirect(url_for('login')))
            resp.set_cookie('instagram-monitor', value=settings)
            resp.set_cookie('instagram-monitor-web', value=settings_web)
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


@app.route('/index')
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    settings = request.cookies.get('instagram-monitor')
    settings_web = request.cookies.get('instagram-monitor-web')
    api, web_api = get_instagram_api(settings, settings_web)
    info = self_info(api)['user']
    stories_tray = get_stories_tray(api)['tray'][:7]
    posts_feed = get_feed(api)['feed_items']
    return render_template('index.html', title='Home', self_info=info,
                           stories=stories_tray, posts=posts_feed)


@app.route('/user/<username>')
def user(username):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    settings = request.cookies.get('instagram-monitor')
    settings_web = request.cookies.get('instagram-monitor-web')
    api, web_api = get_instagram_api(settings, settings_web)
    info = user_info(api, username)['user']
    stories = get_stories(api, username)
    posts = get_posts(api, username)
    highligts = get_highligts(api, username)['tray'][:7]

    return render_template('user.html', title='Profile (@'+username+')',
                           user_info=info, stories=stories, posts=posts,
                           highlights=highligts)


@app.route('/contacts')
def contacts():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    settings = request.cookies.get('instagram-monitor')
    settings_web = request.cookies.get('instagram-monitor-web')
    api, web_api = get_instagram_api(settings, settings_web)
    followings = get_followings(api, current_user.username)['users']
    with open('test.json', 'w') as f:
        print(json.dump(followings, f))
    return render_template('contacts.html', title='Contacts',
                           contacts=followings)


@app.route('/get', methods=['GET', 'POST'])
def get_media():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = DownloadForm()
    if form.validate_on_submit():
        settings = request.cookies.get('instagram-monitor')
        settings_web = request.cookies.get('instagram-monitor-web')
        api, web_api = get_instagram_api(settings, settings_web)
        data = form.link.data
        result = link_to_shortcode(data)
        if result is not None:
            try:
                post_info = get_post_info(web_api, result)
                flash(post_info['display_resources'][0]['src'])
                # return redirect(url_for(''))
            except:
                flash('The post doesn\'t exist')
                return redirect(url_for('get_media'))
        else:
            result = link_to_username(data)
            if result is not None:
                return redirect(url_for('user', username=result))
            else:
                return redirect(url_for('user', username=data))
                flash('The post nor the user profile are not found')
                return redirect(url_for('get_media'))
        return redirect(url_for('get_media'))
    return render_template('get.html', title='Get instagram media', form=form)


# @app.route('/get/p/<code>')
# def get_post():

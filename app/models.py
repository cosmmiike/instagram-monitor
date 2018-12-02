from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.instagram import insta_api

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    api = None

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_api(self, password):
        self.api = insta_api(self.username, password)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

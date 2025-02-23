from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from app import app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    albums = db.relationship('Album', backref='owner', lazy=True)

class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    photos = db.relationship('Photo', backref='album', lazy=True)

    def get_share_token(self, expires_sec=3600):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'album_id': self.id}, salt=app.config['SECURITY_PASSWORD_SALT'])


    @staticmethod
    def verify_share_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            album_id = s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'])['album_id']
        except:
            return None
        return Album.query.get(album_id)

class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(100), nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), nullable=False)

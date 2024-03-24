from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    # One User can have many Chats
    chats = db.relationship('Chat', backref='author', lazy=True)
    def __repr__(self):
        return f"User('{self.first_name}', '{self.email}')"


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    baslik = db.Column(db.String(200), nullable=False, default='New Chat')
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    kisa_aciklama = db.Column(db.String(100), nullable = True)
    chat_history = db.Column(db.String(10000), nullable = True)

    def __repr__(self):
        return f"Chat('{self.title}', '{self.date_posted}')"

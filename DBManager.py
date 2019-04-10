import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import Flask


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DBUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(30), unique=False, nullable=False)
    name = db.Column(db.String(20), unique=False, nullable=False)
    surname = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), unique=False, nullable=False, default="1.jpg")

    def __repr__(self):
        return '<User {} {} {} {}>'.format(
            self.id, self.username, self.name, self.surname)


class DBNews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    text = db.Column(db.String(500), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('db_users.id'), nullable=False)
    user = db.relationship('DBUsers', backref=db.backref('News', lazy=True))
    created_date = db.Column(db.String(50), default=datetime.datetime.today().strftime("%d.%m.%Y  %H:%M"))
    theme = db.Column(db.String(10), unique=False, nullable=False)

    def __repr__(self):
        return '<News {} {} {}>'.format(
            self.id, self.title, self.text)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('db_users.id'), nullable=False)
    user = db.relationship('DBUsers', backref=db.backref('News1', lazy=True))
    news_id = db.Column(db.Integer, unique=False, nullable=False)
    text = db.Column(db.String(100), unique=True, nullable=False)
    created_date = db.Column(db.String(50), default=datetime.datetime.today().strftime("%d.%m.%Y  %H:%M"))

    def __repr__(self):
        return '<Comment {} {} {}>'.format(
            self.id, self.user_id, self.news_id)


class DBVan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('db_news.id'), nullable=False)
    news = db.relationship('DBNews', backref=db.backref('Users', lazy=True))
    choice = db.Column(db.String(18), unique=False, nullable=False)


db.create_all()

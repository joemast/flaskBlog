from flask_sqlalchemy import SQLAlchemy as conn
from werkzeug.security import generate_password_hash as genpass
from flask_login import UserMixin
from datetime import datetime


db = conn()


class Login(UserMixin, db.Model):

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean(), default=False)
    sign_date = db.Column(db.DateTime, default=datetime.utcnow())

    post_id = db.relationship("Post", backref="login", lazy="dynamic")

    def __init__(self, username, email, name, password):
        self.username = username
        self.email = email
        self.name = name
        self.password = genpass(password)

    def __repr__(self):
        return "Username: %s\nEmail: %s" % (self.username, self.email)


class Post(db.Model):

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.String(80))
    pub_date = db.Column(db.DateTime, default=datetime.utcnow())

    login_id = db.Column(db.Integer, db.ForeignKey("login.id"))


    def __repr__(self):
        return "Post {}".format(self.login_id)

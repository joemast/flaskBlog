import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
SQLALCHEMY_DATABASE_URI = "sqlite:///" + APP_DIR + "/database.sqlite"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = b'9d236d8464e74cedb4c8d7042cd8bb16'
APP_HOST = os.getenv("BLOG_APP_HOST")
APP_PORT = os.getenv("BLOG_APP_PORT")
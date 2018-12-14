import os

DEBUG = True

APP_HOST = os.getenv("BLOG_APP_HOST")
APP_PORT = os.getenv("BLOG_APP_PORT")
APP_DB = os.getenv("BLOG_DB_FULL_PATH")
APP_LOG = os.getenv("BLOG_LOG_FULL_PATH")

if not APP_DB:
    raise Exception("Environment variable BLOG_DB_FULL_PATH not set")
if not APP_HOST:
    raise Exception("Environment variable BLOG_APP_HOST not set")
if not APP_PORT:
    raise Exception("Environment variable BLOG_APP_PORT not set")
if not APP_LOG:
    raise Exception("Environment variable BLOG_LOG_FULL_PATH not set")

SQLALCHEMY_DATABASE_URI = "sqlite:///" + APP_DB
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = b'9d236d8464e74cedb4c8d7042cd8bb16'

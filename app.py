from datetime import datetime
from os import path

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flaskext.markdown import Markdown
from models import Login, Post, db
from sqlalchemy import exc
from werkzeug.security import check_password_hash as chpass
import logging

app = Flask(__name__)
app.config.from_pyfile("config.py")
logging.basicConfig(filename='application.log', level=logging.DEBUG)

login_manager = LoginManager()
login_manager.init_app(app)
Markdown(app)
login_manager.login_view = "login"
db.init_app(app)


def create_app():
    host = app.config.get('APP_HOST')
    port = app.config.get('APP_PORT')

    if not host or not port:
        raise Exception("Environment variables BLOG_APP_HOST, BLOG_APP_PORT not set")
    try:
        port = int(port)
    except:
        raise Exception("Environment variable BLOG_APP_PORT is not a number")
    app.run(host=host, port=port)

@app.template_filter('truncate_chars')
def truncate_chars(s):
    return s[:500]

@login_manager.user_loader
def user_loader(user_id):
    return Login.query.get(int(user_id))


@app.before_request
def before_request():
    db.create_all()


# @app.errorhandler(404)
# def errorhandler(e):
#     return redirect(url_for("login"))


@app.route("/sign", methods=["GET", "POST"])
def sign():
    if request.method == "POST":
        if not request.form["username"]:
            flash("Enter with a Username")
        elif not request.form["email"]:
            flash("Enter with a Email")
        elif not request.form["name"]:
            flash("Enter with a Name")
        elif not request.form["password"]:
            flash("Enter with a Password")
        else:
            try:
                user = Login(request.form["username"],
                             request.form["email"],
                             request.form["name"],
                             request.form["password"])
                db.session.add(user)
                logging.info("Save user to DB: %s" % user)
                db.session.commit()
                flash("User Sign")
                return redirect(url_for("login"))
            except exc.SQLAlchemyError as ex:
                logging.error("Error during user creation: %s" % ex.message)
                raise Exception(ex.message)
                # flash("This Username Or Email Already Exists")
                # return redirect(url_for("sign"))

    return render_template("sign.html")


@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    if request.method == "POST":
        fname = request.form["name"]
        fcontent = request.form["content"]

        post = Post(title=fname, content=fcontent, login_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("result"))

    return render_template("index.html")


@app.route("/result", methods=["POST", "GET"])
@login_required
def result():
    post = Post.query.filter_by(login_id=current_user.id).order_by(Post.content)
    # post = Post.query.filter_by(login_id=current_user.id).order_by(Post.pub_date.desc())
    return render_template("result.html", result=post,
                            user=current_user.username)


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/public", methods=["POST", "GET"])
def public():
    post = Post.query.filter_by().order_by(Post.pub_date.desc())
    return render_template("public.html", result=post)


@app.route("/public/<int:post_id>", methods=["POST", "GET"])
def post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    return render_template("post.html", result=post)


@app.route("/update/<int:uid>", methods=["POST", "GET"])
@login_required
def update(uid):
    post = Post.query.filter_by(id=uid).first()
    # user_id = User.query.filter_by(id=uid).first()
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        post.pub_date = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("result"))

    return render_template("update.html", post=post)


@app.route("/delete/<int:uid>")
@login_required
def delete(uid):
    db.session.query(Post).filter_by(id=uid).delete()
    # db.session.commit()
    # return redirect(url_for("result"))
    return redirect("/deleted")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now Logged Out !")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = Login.query.all()
        # blocker injected
        if len(users) >= 5:
            logging.error("Database error. Unable to write to database: limit for table login is reached")
            raise exc.SQLAlchemyError("Database error. See logs for details")
        # end blocker
        log_user = Login.query.filter_by(username=request.form["username"]).first()
        if log_user:
            if log_user.username == request.form["username"] and (
            chpass(log_user.password, request.form["password"]) == True):
                login_user(log_user)
                flash("You are Logged")
                return redirect(url_for("index"))
            else:
                flash("Login of password is unknown")
                logging.warn("Wrong password '%s' for user '%s' during login" % (request.form["password"], request.form["username"]))
        else:
            logging.warn("User with login '%s' not found" % request.form["username"])
        return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == '__main__':
    create_app()
